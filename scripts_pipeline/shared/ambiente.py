"""Descoberta somente leitura do Drive de radio, sem letras fixas ou sync."""
from __future__ import annotations

import argparse
import base64
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata


class DriveIndisponivel(ValueError):
    pass


class DriveAmbiguo(DriveIndisponivel):
    pass


@dataclass(frozen=True)
class DriveRadio:
    raiz_drive: Path
    raiz_radio: Path
    origem: str
    ponto_montagem: Path | None = None
    atalho: Path | None = None

    def serializar(self):
        return {key: str(value) if value is not None else None for key, value in asdict(self).items()}


def _nome(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto.casefold())
                   if not unicodedata.combining(c))


def _filhos(pasta):
    try:
        return list(Path(pasta).iterdir())
    except OSError:
        return []


def _validar_radio(pasta):
    """Exige identidade do acervo e uma pasta anual; nao cria marcadores."""
    pasta = Path(pasta)
    if _nome(pasta.name) != 'radio tjrn conteudo':
        return False
    return any(re.fullmatch(r'00_PRODUCAO_\d{4}', child.name)
               and child.is_dir() for child in _filhos(pasta))


def unidades_disponiveis():
    if os.name == 'nt':
        import ctypes
        kernel = ctypes.windll.kernel32
        mask = kernel.GetLogicalDrives()
        # Nao consulta metadados nem tenta abrir midia removivel sem necessidade.
        return [Path(f'{chr(65+i)}:/') for i in range(26)
                if mask & (1 << i) and kernel.GetDriveTypeW(f'{chr(65+i)}:\\') in (3, 4)]
    home = Path.home()
    return [home / 'Google Drive', home / 'Meu Drive', home / 'My Drive',
            Path('/mnt/google_drive'), Path('/workspace/drive')]


def resolver_atalhos(atalhos):
    """Le TargetPath de .lnk via COM; nunca executa o atalho ou seus argumentos."""
    if os.name != 'nt' or not atalhos:
        return []
    literals = ','.join("'" + str(p).replace("'", "''") + "'" for p in atalhos)
    code = (
        '[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false);'
        '$ErrorActionPreference="Stop";'
        '$shell=New-Object -ComObject WScript.Shell;'
        f'$links=@({literals});'
        '$result=@(foreach($p in $links){try{'
        '$link=$shell.CreateShortcut($p);'
        'if($link.TargetPath -and -not $link.Arguments){[pscustomobject]@{atalho=$p;destino=$link.TargetPath}}'
        '}catch{}});ConvertTo-Json -InputObject $result -Compress'
    )
    encoded = base64.b64encode(code.encode('utf-16-le')).decode('ascii')
    try:
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=12, check=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        targets = json.loads(result.stdout.lstrip('\ufeff').strip())
        if not isinstance(targets, list):
            return []
        allowed = {str(p) for p in atalhos}
        return [(Path(p['atalho']), Path(p['destino'])) for p in targets
                if isinstance(p, dict) and p.get('atalho') in allowed
                and isinstance(p.get('destino'), str) and p['destino']]
    except (OSError, subprocess.SubprocessError, ValueError):
        return []


def _candidatos(raiz):
    raiz = Path(raiz)
    bases = [raiz, raiz / 'Meu Drive', raiz / 'My Drive']
    found = []
    for base in bases:
        if _validar_radio(base):
            found.append((base.parent, base))
        for child in _filhos(base):
            if _validar_radio(child):
                found.append((base, child))
    return found


def descobrir_drive(*, env=None, raizes=None, resolver=None):
    env = os.environ if env is None else env
    override = env.get('AGENTE_RADIO_DRIVE_ROOT') or env.get('DIVISOR_DRIVE_ROOT')
    found = []

    def add(root, origem, ponto_montagem=None, atalho=None):
        for drive, radio in _candidatos(root):
            radio = radio.resolve()
            if any(radio == item.raiz_radio for item in found):
                continue
            found.append(DriveRadio(drive.resolve(), radio, origem, ponto_montagem, atalho))

    if override:
        add(Path(override).expanduser(), 'configuracao')
        if len(found) == 1:
            return found[0]
        if len(found) > 1:
            raise DriveAmbiguo('A configuracao aponta para varios acervos de radio.')
    roots = list(unidades_disponiveis() if raizes is None else raizes)
    links = []
    for root in roots:
        root = Path(root)
        add(root, 'unidade', ponto_montagem=root)
        for name in ('Meu Drive.lnk', 'My Drive.lnk'):
            link = root / name
            if link.is_file():
                links.append(link)
    for resolved in (resolver or resolver_atalhos)(links):
        if isinstance(resolved, tuple):
            link, target = resolved
            add(target, 'atalho', ponto_montagem=Path(link).parent, atalho=Path(link))
        else:
            add(resolved, 'atalho')
    if len(found) > 1:
        raise DriveAmbiguo('Mais de um acervo valido. Defina AGENTE_RADIO_DRIVE_ROOT: '
                          + '; '.join(str(item.raiz_radio) for item in found))
    if not found:
        suffix = f' Configuracao indisponivel: {override}.' if override else ''
        raise DriveIndisponivel('Drive de radio nao localizado ou sem permissao. '
                               'Monte o Drive ou defina AGENTE_RADIO_DRIVE_ROOT.' + suffix)
    return found[0]


def inicializar_ambiente(*, obrigatorio=False, env=None, raizes=None, resolver=None, log=True):
    """Atualiza apenas o processo atual; local/nuvem continuam sem Drive se opcional."""
    env = os.environ if env is None else env
    try:
        drive = descobrir_drive(env=env, raizes=raizes, resolver=resolver)
    except DriveIndisponivel as exc:
        result = {'status': 'ambiguo' if isinstance(exc, DriveAmbiguo) else 'indisponivel',
                  'mensagem': str(exc)}
        # Nao deixa uma descoberta anterior parecer valida depois de desmontagem.
        env.pop('AGENTE_RADIO_RADIO_ROOT', None)
        if log:
            print('agente_radio: ' + str(exc), file=sys.stderr)
        if obrigatorio:
            raise
        return result
    # DRIVE_ROOT e override de entrada: nao sobrescrever com cache da descoberta.
    env['AGENTE_RADIO_RADIO_ROOT'] = str(drive.raiz_radio)
    result = {'status': 'disponivel', **drive.serializar()}
    override = env.get('AGENTE_RADIO_DRIVE_ROOT') or env.get('DIVISOR_DRIVE_ROOT')
    if override and drive.origem != 'configuracao':
        result['aviso'] = f'Caminho configurado indisponivel: {override}; descoberta automatica utilizada.'
    if log:
        print('agente_radio: Drive validado em ' + str(drive.raiz_radio), file=sys.stderr)
        if result.get('aviso'):
            print('agente_radio: ' + result['aviso'], file=sys.stderr)
    return result


def pasta_boletins_drive(ano, *, env=None):
    """Resolve a fonte; nunca deduz ou cria destinos de publicacao."""
    if not re.fullmatch(r'\d{4}', str(ano)):
        raise ValueError('Ano invalido.')
    drive = descobrir_drive(env=env)
    path = drive.raiz_radio / f'00_PRODUCAO_{ano}' / '01_BOLETINS_DIARIOS' / '03_AUDIOS_RADIO'
    if not path.is_dir():
        raise DriveIndisponivel(f'Fonte de boletins inexistente ou inacessivel: {path}')
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--obrigatorio', action='store_true')
    parser.add_argument('--buscar', type=Path, action='append')
    args = parser.parse_args(argv)
    result = inicializar_ambiente(raizes=args.buscar, log=not args.json)
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    return 2 if args.obrigatorio and result['status'] != 'disponivel' else 0


if __name__ == '__main__':
    raise SystemExit(main())

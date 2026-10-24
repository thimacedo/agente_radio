"""Mudancas de letra, atalhos e ausencia do Drive, sem tocar acervo real."""
from pathlib import Path

import pytest

from shared import ambiente


def acervo(root):
    radio = root / 'Meu Drive' / 'RADIO TJRN CONTEÚDO'
    (radio / '00_PRODUCAO_2026').mkdir(parents=True)
    return radio


def test_localiza_em_qualquer_unidade_sem_criar_arquivos(tmp_path):
    old = tmp_path / 'G'
    new = tmp_path / 'I'
    old.mkdir()
    radio = acervo(new)
    before = set(tmp_path.rglob('*'))
    result = ambiente.descobrir_drive(env={}, raizes=[old, new])
    assert result.raiz_radio == radio
    assert result.raiz_drive == new / 'Meu Drive'
    assert set(tmp_path.rglob('*')) == before


def test_override_valido_tem_prioridade(tmp_path):
    selected = acervo(tmp_path / 'selecionado')
    other = acervo(tmp_path / 'outro')
    result = ambiente.descobrir_drive(env={'AGENTE_RADIO_DRIVE_ROOT': str(selected)}, raizes=[other])
    assert result.raiz_radio == selected
    assert result.origem == 'configuracao'


def test_override_obsoleto_redescobre_sem_mudar_configuracao(tmp_path):
    radio = acervo(tmp_path / 'I')
    env = {'AGENTE_RADIO_DRIVE_ROOT': str(tmp_path / 'G')}
    result = ambiente.inicializar_ambiente(env=env, raizes=[tmp_path / 'I'], log=False)
    assert result['status'] == 'disponivel'
    assert 'aviso' in result
    assert env['AGENTE_RADIO_RADIO_ROOT'] == str(radio)
    assert env['AGENTE_RADIO_DRIVE_ROOT'] == str(tmp_path / 'G')


def test_duas_contas_nao_escolhe_automaticamente(tmp_path):
    acervo(tmp_path / 'I')
    acervo(tmp_path / 'J')
    with pytest.raises(ambiente.DriveAmbiguo):
        ambiente.descobrir_drive(env={}, raizes=[tmp_path / 'I', tmp_path / 'J'])


def test_segue_atalho_sem_executar_arquivo(tmp_path):
    volume = tmp_path / 'I'
    volume.mkdir()
    link = volume / 'Meu Drive.lnk'
    link.write_bytes(b'atalho-falso')
    radio = acervo(tmp_path / 'espelho')
    def resolve(links):
        assert links == [link]
        return [(link, radio.parent)]
    result = ambiente.descobrir_drive(env={}, raizes=[volume], resolver=resolve)
    assert result.raiz_radio == radio
    assert result.origem == 'atalho'
    assert result.ponto_montagem == volume
    assert result.atalho == link


def test_atalho_e_caminho_direto_deduplicados(tmp_path):
    root = tmp_path / 'I'
    radio = acervo(root)
    (root / 'Meu Drive.lnk').write_bytes(b'x')
    assert ambiente.descobrir_drive(env={}, raizes=[root], resolver=lambda _: [radio.parent]).raiz_radio == radio


def test_pasta_so_com_nome_nao_e_acervo(tmp_path):
    (tmp_path / 'RADIO TJRN CONTEÚDO').mkdir()
    with pytest.raises(ambiente.DriveIndisponivel):
        ambiente.descobrir_drive(env={}, raizes=[tmp_path])


def test_sem_drive_na_nuvem_continua_local_e_limpa_cache(tmp_path):
    env = {'AGENTE_RADIO_RADIO_ROOT': 'obsoleto'}
    result = ambiente.inicializar_ambiente(env=env, raizes=[tmp_path], log=False)
    assert result['status'] == 'indisponivel'
    assert 'AGENTE_RADIO_RADIO_ROOT' not in env
    with pytest.raises(ambiente.DriveIndisponivel):
        ambiente.inicializar_ambiente(env={}, raizes=[tmp_path], obrigatorio=True, log=False)


def test_redescobre_depois_que_unidade_muda(tmp_path):
    old, new = tmp_path / 'G', tmp_path / 'I'
    acervo(old)
    env = {}
    ambiente.inicializar_ambiente(env=env, raizes=[old, new], log=False)
    old.rename(new)
    ambiente.inicializar_ambiente(env=env, raizes=[old, new], log=False)
    assert env['AGENTE_RADIO_RADIO_ROOT'] == str(new / 'Meu Drive' / 'RADIO TJRN CONTEÚDO')


def test_diagnostico_json_nao_aprova_drive_ausente(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv('AGENTE_RADIO_DRIVE_ROOT', raising=False)
    monkeypatch.delenv('DIVISOR_DRIVE_ROOT', raising=False)
    assert ambiente.main(['--json', '--obrigatorio', '--buscar', str(tmp_path)]) == 2
    assert '"status": "indisponivel"' in capsys.readouterr().out


def test_fonte_exige_pasta_real_do_ano(tmp_path, monkeypatch):
    radio = acervo(tmp_path / 'I')
    source = radio / '00_PRODUCAO_2026/01_BOLETINS_DIARIOS/03_AUDIOS_RADIO'
    source.mkdir(parents=True)
    monkeypatch.setattr(ambiente, 'unidades_disponiveis', lambda: [])
    env = {'AGENTE_RADIO_DRIVE_ROOT': str(radio)}
    assert ambiente.pasta_boletins_drive(2026, env=env) == source
    with pytest.raises(ambiente.DriveIndisponivel):
        ambiente.pasta_boletins_drive(2027, env=env)


def test_letra_nova_nao_reaproveita_cache_de_saida(tmp_path):
    env = {'AGENTE_RADIO_RADIO_ROOT': str(acervo(tmp_path / 'antigo'))}
    radio = acervo(tmp_path / 'novo')
    result = ambiente.inicializar_ambiente(env=env, raizes=[tmp_path / 'novo'], log=False)
    assert result['raiz_radio'] == str(radio)

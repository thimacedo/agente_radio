# Descoberta do Drive na inicializacao

O agente_radio nao pressupoe que o Google Drive seja H:, G: ou I:.
Antes do backend, dos comandos operacionais de dev.ps1 e das CLIs canonicas
de BOLETIM, NJUD e GIRO, verifica onde esta o acervo de radio.

```powershell
./dev.ps1 ambiente
./dev.ps1 ambiente --obrigatorio
```

O primeiro comando retorna JSON sem alterar arquivos. O segundo retorna
codigo 2 quando nao ha um Drive validado. Backend e processamento local
continuam disponiveis sem Drive: a resposta /health inclui o estado do Drive
separadamente. Uma operacao que requer a fonte do Drive deve usar
shared.ambiente.pasta_boletins_drive(ano), que falha antes de copiar se a
fonte nao existir. A localizacao de destinos de publicacao continua explicita;
descobrir o Drive nao autoriza publicar nem aprova conteudo.

## Como a descoberta funciona

1. Respeita AGENTE_RADIO_DRIVE_ROOT (ou o alias DIVISOR_DRIVE_ROOT), se apontar
   para um acervo valido. Pode ser uma unidade, pasta Meu Drive/My Drive ou
   a propria pasta RADIO TJRN CONTEUDO, com ou sem acentos.
2. Se o caminho configurado estiver indisponivel, procura novamente e avisa
   sobre o fallback. Nao modifica o arquivo de configuracao nem grava cache.
3. No Windows consulta unidades fixas/de rede e os diretorios imediatos.
   Nao percorre discos inteiros, nem consulta midias removiveis.
4. Reconhece Meu Drive.lnk e My Drive.lnk, lendo apenas TargetPath via COM.
   Nao executa o atalho; atalhos com argumentos sao ignorados.
5. Exige uma pasta RADIO TJRN CONTEUDO contendo ao menos uma pasta anual
   00_PRODUCAO_AAAA. Para obter os boletins, valida tambem a fonte do ano.
6. Deduplica caminhos resolvidos. Se houver dois acervos distintos, nao
   escolhe silenciosamente: informa ambiguidade e pede configuracao explicita.

Na nuvem, pode-se apontar AGENTE_RADIO_DRIVE_ROOT para um acervo montado ou
copiado com a mesma estrutura. Sem esse recurso, o diagnostico informa
indisponivel e os trabalhos com entradas locais explicitas continuam.
A descoberta nao monta volumes, baixa arquivos ou usa credenciais de conectores.

Para uma busca dirigida:

```powershell
./dev.ps1 ambiente --buscar 'I:\' --obrigatorio
```

AGENTE_RADIO_RADIO_ROOT e a saida da descoberta para o processo atual, nunca
uma fonte de verdade persistente. Cada nova inicializacao verifica os caminhos
novamente. Os subprocessos recebem a variavel; ela e restaurada no chamador
ao sair do wrapper PowerShell. Variaveis de destino como DRIVE_SYNC nao sao
reescritas por heuristica.

## Computador base verificado em 24/10/2026

I: tem rotulo Google Drive. Seu atalho Meu Drive.lnk aponta para
E:\h\Meu Drive, onde foi validada a pasta RADIO TJRN CONTEUDO (com acentos no
nome real). G: tem rotulo CARRO. Esses dados sao um registro de verificacao;
o programa descobre novamente em cada inicializacao e nao os usa como default.

Arquivos brutos, caches, audios finais, manifestos e registros antigos nao
tem suas referencias substituidas em massa. O script de importacao GIRO
giro_sync_h_para_workspace.py mantem o nome por compatibilidade, mas sua fonte
agora e descoberta; a descoberta em si nao executa importacao ou sincronizacao.

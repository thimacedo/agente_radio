# Migracao para agente_radio

Nome adotado em 24/10/2026. O sistema abrange BOLETIM, NJUD e GIRO nas Comarcas.

## Executado e verificado

- Repositorio renomeado de thimacedo/agente_njud para thimacedo/agente_radio,
  preservando o ID R_kgDOUC5MEg, o historico e os PRs existentes.
- PR de identidade #7 integrado; interface, API e documentacao usam agente_radio.
- Checkout movido de E:\02_Projetos_Trabalho\Projetos_Ativos\DIVISOR para
  E:\02_Projetos_Trabalho\Projetos_Ativos\agente_radio no mesmo diretorio-pai.
- origin atualizado para https://github.com/thimacedo/agente_radio.git.
- Excecao Git safe.directory adicionada somente para a nova pasta. O volume
  nao registra proprietario, e o Git exigiu a excecao apos a renomeacao.
- Python 3.11 da venv existente executou a partir da pasta nova.
- Alteracao local anterior em etapa_triagem.py preservada, fora do commit de
  migracao. SHA256: C73D4315CC23E71FF266A58B575E416A2200BC2E49C698D7760334AB1BF6B929.
- Descoberta de Drive adicionada; ver DRIVE_AUTOMATICO.md. Nao se troca G: por
  I: em massa, pois G: agora e outro dispositivo e Meu Drive em I: e um atalho.

## Compatibilidade e preservacao

Variaveis DIVISOR_* e identificadores internos existentes continuam funcionando.
Nomes dos programas, audios entregues, fontes, manifestos, caches, hashes e
auditorias nao sao renomeados. Referencias em proveniencia historica ficam como
foram registradas. A mudanca de nome nao sincroniza automaticamente outros
checkouts ou ambientes em nuvem.

## Referencias externas que exigem tratamento separado

A tarefa agendada DIVISOR Painel aponta para F:\Projetos\DIVISOR, com outro
ambiente Python e src/tools/dashboard.py. Nao foi redirecionada para o backend
atual: nao ha evidencia de que esse painel legado seja equivalente. A tarefa
foi apenas inventariada e preservada.

Documentos antigos ainda podem descrever src/ e caminhos historicos. Na revisao
atual, as implementacoes canonicas ficam em scripts_pipeline/boletim,
scripts_pipeline/njud e scripts_pipeline/giro. Nao restaure modulos antigos
por causa desses exemplos. Outros checkouts devem ser inventariados antes de
atualizar seus remotos ou caminhos.

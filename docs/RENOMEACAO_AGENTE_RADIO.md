# Migração para agente_radio

Nome adotado pelo usuário em 24/10/2026: `agente_radio`.
Escopo do sistema: BOLETIM, NJUD e GIRO nas Comarcas.

## Etapa preparada neste PR

- Identidade visual da interface, título da API e documentação principal.
- Valor de exemplo de PROJETO_NOME atualizado.
- Nenhuma alteração nos algoritmos, nos nomes dos programas ou nos áudios.
- Caminhos operacionais e variáveis DIVISOR_* mantidos para compatibilidade.

## Situação verificada

O repositório remoto ainda se chama thimacedo/agente_njud.
O checkout local foi identificado historicamente em
E:\02_Projetos_Trabalho\Projetos_Ativos\DIVISOR.
A inspeção atual do disco ficou indisponível; a presença, o estado Git e os
caminhos desse checkout precisam de confirmação antes da movimentação.
Há alterações e produção registradas em outros ambientes que não devem ser
substituídas por uma cópia da main remota.

## Ordem de conclusão

1. Inventariar cada checkout, HEAD, remoto, alterações sem commit e arquivos não
   rastreados. Preservar ajustes e fontes; não executar reset, clean ou pull
   automático.
2. Buscar referências operacionais a DIVISOR e agente_njud em scripts, configs,
   serviços, tarefas agendadas, atalhos e automações. Não imprimir segredos.
3. Registrar processos ativos e seus diretórios. Fazer a troca de pasta em uma
   janela sem produção ativa.
4. Renomear o repositório existente para thimacedo/agente_radio nas configurações
   do GitHub, preservando o mesmo ID, issues, PRs e histórico. Confirmar a URL nova
   e o redirecionamento da antiga.
5. Verificar que a pasta de destino não existe e que a origem resolvida é o
   checkout correto. Renomear a pasta local no mesmo diretório-pai para
   agente_radio, preservando o conteúdo.
6. Atualizar origin em cada checkout após confirmar a URL nova. Ajustar caminhos
   externos inventariados e BASE_DIR no ambiente real. Não sobrescrever .env.
7. Verificar a portabilidade da venv após a mudança de caminho; recriar apenas
   quando necessário, preservando a anterior e registrando dependências.
8. Adicionar nomes AGENTE_RADIO_* com fallback às variáveis DIVISOR_* usadas pelo
   código. Só trocar nomes internos de módulos com atualização dos imports.
9. Executar verificações de ambiente, testes pertinentes, health e upload
   simulado. Validar áudio real em saída isolada antes de retomar produção.
10. Confirmar URLs, caminhos, hashes dos arquivos preservados e pendências por
    ambiente. Renomear o repositório não sincroniza os checkouts automaticamente.

## Preservação

Nomes de BOLETIM, NJUD e GIRO, áudios entregues, fontes, manifestos, hashes,
auditorias e registros históricos permanecem intactos. Referências antigas em
proveniência não devem ser substituídas em massa. Documentação histórica pode
mencionar o nome anterior; documentação operacional vigente será atualizada
depois da conferência dos caminhos reais.

## Reversão

Guardar caminho e remoto anteriores no inventário. Em caso de falha, restaurar
caminhos e configurações a partir desse registro, sem apagar versões ou fontes.
A reversão do nome no GitHub exige verificar antes a disponibilidade do nome
anterior. Não usar substituição global em arquivos binários, caches ou venvs.

# Atualização do fluxo para 0.2.0

Comparação entre a base 0.1.0 e o fluxo de referência, incluindo o refinamento de QA de setembro de 2026. Somente práticas reutilizáveis foram incorporadas.

| Tema | Template 0.1.0 | Fluxo de referência | Adaptação no template |
| --- | --- | --- | --- |
| Entrada | Skills isoladas; sem Supervisor | Sessão principal coordena quatro papéis | Skill supervisor reconhece criação, preparação, atualização e continuidade |
| Projeto novo | project-create exige stack escolhida | Supervisor começa num projeto já preparado | Supervisor coleta objetivo/destino; stack pode ficar a definir ou não se aplicar |
| Projeto existente | bootstrap e update são citados, mas não existem | Skills para ambos os casos | Workflows pequenos, preservando trabalho e revisando mudanças |
| Revisão | Procedimento geral de revisão | Contexto frio, execução própria e identidades distintas | Independência explícita; relato e CI não bastam |
| Unidade de trabalho | Task e SDD opcional | Tarefas compõem uma milestone | Uma entrega verificável, inclusive de uma única tarefa |
| QA | Sem papel funcional | Suíte como pré-condição; história vivida de ponta a ponta | História proporcional para UI, CLI, dados ou documento |
| Versão testada | Sem manifesto de candidato | SHAs por repositório e ambiente fixado | SHAs mais hashes locais, ou hashes de artefatos sem Git |
| Passagem | Relato livre | Task, PR, base, HEAD, resultado e evidência | Modelo compartilhado com independência, lacunas e próximo responsável |
| Git | Nova branch a partir de main | Feature → develop → main | main continua padrão; develop só por adoção aprovada |
| Autorizações | Aprovação para ações protegidas e externas | Autorizações específicas concedidas ao projeto | Nenhuma autorização herdada; política local preservada |
| Descoberta | Skills geradas para dois agentes | Configurações nativas e modelos por papel | Skills portáteis; nenhuma alteração global ou modelo fixo |

## Generalização

Foram excluídos nomes de empresa e pessoas, domínio comercial, nicho, personas reais, tarefas e milestones reais, links para decisões específicas, caminhos da máquina de origem, lista de serviços, branches de produção particulares, identificadores de Apps, contas, domínios, chaves, ferramentas de credenciais, infraestrutura, pendências e histórico de incidentes particulares.

Ferramentas de testes, modelos, limites de experiência e forma de hospedagem viraram decisões do projeto. Regras de ferramenta não foram transformadas em proibições universais.

A fonte de referência foi consultada somente para leitura. Configuração declarativa descreve intenção; não prova que integração, identidade, proteção ou ambiente está ativo.

## Verificação do Supervisor

Cenários em [evals/tasks](../../../evals/tasks/03-supervisor-entrada.md) cobrem chamada isolada, criação sem stack, projeto que não é software, destino ocupado, raiz com vários repositórios, falta de delegação e mudança de candidato.

A validação estrutural confirma arquivos, referências, workflow e cópias de skills. Avaliação comportamental verifica as decisões com pedidos realistas. Nenhuma avaliação representa publicação de um projeto nem teste de uma integração externa inexistente.

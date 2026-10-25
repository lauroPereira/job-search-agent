<!-- Papel: explicar a finalidade de docs/architecture/ e do registro de decisões arquiteturais. -->

# docs/architecture/

Documentação da arquitetura do projeto: estrutura, limites entre componentes, fluxos principais e as decisões que moldaram tudo isso.

## decisions/

`docs/architecture/decisions/` guarda os registros de decisão arquitetural (ADR). Cada arquivo captura uma decisão com título, status, contexto, decisão tomada, alternativas consideradas, consequências e data.

Registre uma decisão quando a escolha for estrutural e cara de reverter: banco de dados, protocolo de comunicação, limite entre módulos, dependência central, estratégia de autenticação, formato de dado consumido externamente.

Não registre preferências triviais nem detalhes de implementação que o próprio código já expressa com clareza.

Use `docs/templates/decision-record.md` como ponto de partida. Nomeie os arquivos com prefixo numérico sequencial, por exemplo `0001-usar-postgresql.md`.

Decisões são imutáveis depois de aceitas: quando uma decisão deixa de valer, crie um novo registro que a substitua e marque o anterior como substituído, em vez de reescrever o histórico.

## Propriedade dos arquivos

Este diretório pertence ao projeto. Os registros de decisão são conteúdo do projeto; apenas este README, o marcador de `decisions/` e os modelos em `docs/templates/` são gerenciados pelo template.

## Relacionados

- `docs/templates/decision-record.md` — modelo de registro de decisão.
- `docs/specs/` — especificações e a regra de quando aplicar SDD.

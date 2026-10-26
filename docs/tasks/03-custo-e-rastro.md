# Tarefa: mascaramento, custo, limites e rastro

## Objetivo

Calcular tokens e custo de cada chamada de modelo, preparar os limites por turno e por dia e gravar o rastro mascarado em SQLite.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Custo" e "Rastro local". Critérios da especificação: "toda resposta mostra tokens e custo; o rastro de uma conversa pode ser aberto localmente"; requisito não funcional de privacidade (logs mascaram dados pessoais).

## Pré-condições

Tarefa 01 concluída.

## Arquivos prováveis

`src/job_search_agent/masking.py`, `src/job_search_agent/costs.py`, `src/job_search_agent/traces.py`, `config.example.toml` (`[masking] names`, `[limits]`), `tests/test_masking.py`, `tests/test_costs.py`, `tests/test_traces.py`.

## Passos

1. `masking.py`: e-mail, telefone, CPF e números longos, links de perfil pessoal e os nomes de `[masking] names` da configuração (comparação sem acento e sem maiúscula). No exemplo de configuração, os nomes fictícios do seed.
2. `costs.py`: custo a partir de `usage_metadata` (entrada, entrada em cache, saída) e da tabela de preços; soma por turno; comparação com `max_tokens_per_turn`; verificação de `max_tokens_per_day`.
3. Configuração dos limites: `recursion_limit`, `max_output_tokens`, `max_tokens_per_turn`, `max_tokens_per_day` (valores iniciais do plano).
4. `traces.py`: tabelas `turns` e `steps` (decisões de aprovação como `kind = approval`); gravação mascarada; total de tokens do dia; custo por dia para o dashboard.

## Critérios de conclusão

- [x] Testes de mascaramento com exemplos sintéticos de cada padrão e de um nome da lista.
- [x] Teste de custo com uso fictício e preços da configuração (incluindo entrada em cache).
- [x] Teste: limite do dia excedido é detectado a partir do rastro; uso do turno acima de `max_tokens_per_turn` é marcado.
- [x] Teste: um turno gravado aparece em `turns` e `steps`, sem texto pessoal não mascarado.

## Validação

Executada em 2026-10-25, Windows 11, `.venv` com Python 3.12 (versões da tarefa 01, sem mudança).

**Implementação**

- `masking.py`: `mask(text, names)` troca e-mail (`[email]`), link de perfil pessoal (LinkedIn, GitHub, Instagram, Facebook, X/Twitter: `[perfil]`), CPF com ou sem pontuação (`[cpf]`), telefone brasileiro com DDD opcional e separador (`[telefone]`) e outros números de 8 ou mais dígitos (`[numero]`). Os nomes da lista são procurados no texto "dobrado" (sem acento e minúsculo, uma letra por letra, mesmas posições) e trocados por `[pessoa]` no original; o nome casa só como palavra inteira ("Ana Exemplar" e "Anaconda" ficam). Nomes de empresas, datas (`2026-03-16`) e notas ficam.
- `costs.py`: `Usage` (entrada, saída, entrada em cache) lido de `usage_metadata` (`input_token_details.cache_read`); `cost_usd` cobra a parte em cache pelo preço `cached_input` e o resto da entrada pelo `input` (a entrada informada pela API já inclui a parte em cache); embeddings só têm `input`; modelo sem preço é erro, nunca custo zero. Soma por turno com `sum(usages, Usage())`; `over_turn_limit` (acima de `max_tokens_per_turn`) e `day_limit_reached` (`>= max_tokens_per_day`).
- Configuração dos limites: `recursion_limit`, `max_output_tokens`, `max_tokens_per_turn` e `max_tokens_per_day` e a lista `[masking] names` (nomes fictícios do seed) já estavam em `config.example.toml` e validados em `config.py` desde a tarefa 01; nada mudou ali.
- `traces.py`: `TraceStore(path, names)` cria `turns` e `steps` com as colunas do plano; `start_turn`, `add_step` (`kind` em `model`, `tool`, `approval`; `origin` em `chat`, `dashboard`), `finish_turn`, `turn`, `steps`, `tokens_on(dia)` (entrada + saída dos turnos do dia, data local) e `cost_by_day(início, fim)` para o dashboard. Texto da pessoa mascarado; `args` e `result` em JSON, mascarados e cortados em 500 caracteres.

**Decisões**

- Coluna extra `turns.over_turn_limit` (0 ou 1): o critério pede que o turno acima de `max_tokens_per_turn` seja marcado, e o plano não listava onde. É a única diferença em relação às colunas do plano.
- `started_at` gravado em hora local com fuso (ISO 8601); o "dia" do limite diário e do custo por dia é a data local.
- Um CPF sem pontuação e um celular sem separador têm os mesmos 11 dígitos: os dois viram `[cpf]`. Para o rastro e o índice basta que fiquem mascarados.
- `steps.turn_id` é obrigatório; como o dashboard registra seus passos (origem `dashboard`) fica para a tarefa 08.

**Testes** (`tests/test_masking.py`, `tests/test_costs.py`, `tests/test_traces.py`, 27 testes novos):

- mascaramento: um exemplo sintético de cada padrão; nome da lista com maiúsculas, espaços extras e acentos trocados; nome acentuado da lista achado em texto sem acento; empresa, data, nota e palavras parecidas preservadas.
- custo: `usage_metadata` com `cache_read`; custo do `gpt-6.1-sol` com entrada em cache pelos preços da configuração de exemplo; embeddings só com entrada; modelo sem preço; soma de três chamadas acima de `max_tokens_per_turn`; limite do dia.
- rastro: um turno com passos `model`, `tool` e `approval` aparece em `turns` e `steps`, e o `iterdump()` do arquivo não contém o nome, o e-mail, o telefone nem o CPF do pedido (contém `[pessoa]`, `[email]` e "Banco Aurora"); limite do dia detectado a partir do rastro (turnos de outro dia não contam); turno acima do limite marcado; custo por dia; resumo longo cortado; `kind` e `status` inválidos recusados.

```text
.venv\Scripts\python.exe tools/scripts/lint_and_tests.py --strict   -> 58 passed; ruff limpo; validação estrita sem falhas
.venv\Scripts\python.exe -m ruff format --check src tests          -> 16 files already formatted
```

> **Achados da revisão (PR 5), corrigidos no mesmo PR:**
>
> - (Média) O padrão de telefone apagava intervalos de anos e pares de números ("Trabalhei de 2019-2023", "Período 2019 2023", "teste 1234 5678" viravam `[telefone]`). Agora o celular exige o prefixo 9 seguido de 8 dígitos (DDD opcional) e o número de 8 dígitos exige DDD explícito; um par de anos `(19|20)\d\d[-\s](19|20)\d\d` nunca é telefone. Um número de 8 dígitos sem DDD ("3456-7890") deixa de ser mascarado.
> - (Baixa) `traces.summarize` mascara cada texto (chaves incluídas) antes do `json.dumps` e o JSON mais uma vez depois: um nome com quebra de linha não escapa mais como `\n`.
> - (Baixa) Telefones e CPF em outras formas: "11 9 8765-4321" (espaço depois do 9) e "+5511987654321" viram `[telefone]` (antes, o segundo virava `+[numero]`); CPF com espaços "123 456 789 09" vira `[cpf]`.
> - (Baixa) `config.example.toml`: comentário em `[masking] names` dizendo que, no uso real, os primeiros nomes que aparecem sozinhos também entram na lista.
>
> Testes novos: `test_other_phone_and_cpf_forms_are_masked` (6 casos), `test_year_ranges_and_number_pairs_stay` (5 casos, entre eles os anos da revisão e o fixo sem DDD) e `test_name_with_line_break_is_masked_before_the_json`; os exemplos de telefone que já passavam continuam em `test_each_pattern_is_masked`.
>
> Validação depois das correções: `lint_and_tests.py --strict` com 70 testes passando, ruff limpo, `ruff format --check src tests` limpo.

## Status

```text
concluída
```

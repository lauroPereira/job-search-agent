# 0002. Ações externas ficam com a pessoa

## Título

O agente redige, consulta e propõe; enviar, publicar, entrar em contas, aceitar termos e responder avaliações ficam sempre com a pessoa.

## Status

```text
aceita
```

Aceita pelo autor em 2026-10-25 (decisão A6 do [modelo de domínios](https://github.com/lauroPereira/job-search-mcp/blob/develop/docs/specs/modelo-de-dominios.md) do servidor).

## Contexto

Em 25 dias de uso real com agentes de IA na recolocação, as mesmas regras foram impostas em todas as sessões: nada enviado sem revisão, nenhum login feito pelo agente, nenhuma resposta a teste ou prova, aceite de termos só pela pessoa, acesso a e-mail só para leitura. Quando o agente passou do limite (respondeu uma pergunta avaliativa, gravou um status por suposição), o custo foi alto e difícil de desfazer.

## Decisão

O sistema não tem, e não ganha, capacidade de:

- enviar mensagens, e-mails, candidaturas ou convites, ou publicar posts;
- fazer login, criar contas, preencher dados pessoais sensíveis ou documentos;
- aceitar termos, consentimentos ou cookies;
- responder testes, provas ou perguntas avaliativas;
- gravar dados sem a confirmação da proposta pelo servidor.

O que o sistema faz: consultar o servidor e a base de conhecimento, redigir textos para a pessoa revisar e enviar, e propor alterações que a pessoa confirma ou recusa.

Regras de conteúdo que acompanham a redação:

- honestidade de autoria: trabalho de equipe descrito como de equipe; nenhuma competência, número ou resultado afirmado sem base;
- fatos (datas, cargos, números) vêm do servidor, não da memória do modelo;
- discrição: não citar um contato como fonte de informação para outro.

## Alternativas consideradas

- **Envio automático com aprovação prévia.** Descartada: um clique a mais não compensa o risco de mensagem errada em canal pessoal, e exigiria credenciais no sistema.
- **Leitura automática de Gmail, WhatsApp e LinkedIn.** Adiada: exige credenciais e amplia a superfície de dados pessoais; os fatos entram colados no chat.

## Consequências

- O case mostra guardrails como propriedade do desenho, não como promessa: não existem ferramentas para essas ações.
- A pessoa continua com o trabalho manual de enviar e publicar, que é intencional.
- Casos de avaliação incluem pedidos que devem ser recusados (por exemplo, "envie esta mensagem").

## Data

2026-10-25

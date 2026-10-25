<!-- Papel: explicar a finalidade de docs/specs/ e a regra de quando aplicar o fluxo de SDD. -->

# docs/specs/

Especificações de mudanças relevantes: o que precisa ser resolvido e por quê, antes de decidir como implementar.

Uma especificação descreve problema, usuário afetado, resultado desejado, escopo, requisitos, casos de uso, critérios de aceitação, riscos e questões em aberto. Ela não descreve solução técnica — isso pertence ao plano.

Use `docs/templates/spec.md` como ponto de partida. Um arquivo por especificação, em kebab-case, por exemplo `checkout-com-cupom.md`.

Este diretório pertence ao projeto. Os arquivos de especificação são conteúdo do projeto; apenas este README e os modelos em `docs/templates/` são gerenciados pelo template.

## Quando aplicar SDD

O SDD deste template é opcional e proporcional ao impacto da mudança. Não transforme toda alteração em processo.

```text
mudança pequena:
task ou alteração direta

mudança relevante:
spec → plan → tasks → implementação → validação

decisão arquitetural:
decision-record
```

- **Mudança pequena** — correção localizada, ajuste de texto, refatoração sem efeito externo. Vá direto à alteração, ou registre uma task quando o trabalho for dividido em etapas.
- **Mudança relevante** — comportamento novo, contrato público, dados, permissões, integração externa ou trabalho que atravessa vários componentes. Escreva a especificação, derive o plano, quebre em tasks, implemente e valide.
- **Decisão arquitetural** — escolha estrutural com consequências duradouras, como banco, protocolo, limite de módulo ou dependência central. Registre um decision record em `docs/architecture/decisions/`.

Na dúvida sobre a classificação, pergunte ao usuário em vez de presumir.

## Relacionados

- `docs/templates/spec.md` — modelo de especificação.
- `docs/templates/plan.md` — modelo de plano técnico derivado de uma especificação.
- `docs/tasks/` — tarefas executáveis derivadas de um plano.
- `docs/architecture/decisions/` — decisões arquiteturais registradas.

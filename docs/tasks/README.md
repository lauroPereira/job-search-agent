<!-- Papel: explicar a finalidade de docs/tasks/ e como uma tarefa deve ser escrita para execução por agentes. -->

# docs/tasks/

Tarefas executáveis: unidades de trabalho pequenas e verificáveis, derivadas de um plano ou criadas diretamente para mudanças pequenas.

Uma tarefa descreve objetivo, especificação relacionada, pré-condições, arquivos prováveis, passos, critérios de conclusão, validação e status. Ela deve ser executável por um agente sem conhecimento implícito essencial.

Use `docs/templates/task.md` como ponto de partida. Um arquivo por tarefa, em kebab-case, por exemplo `validar-cupom-expirado.md`.

Boas tarefas são estreitas: se uma tarefa toca muitos componentes ou depende de decisões ainda não tomadas, ela provavelmente precisa de uma especificação antes, não de mais detalhamento.

Este diretório pertence ao projeto. Os arquivos de tarefa são conteúdo do projeto; apenas este README e os modelos em `docs/templates/` são gerenciados pelo template.

## Status

Mantenha o campo de status atualizado no próprio arquivo:

```text
pendente | em andamento | concluída | bloqueada | cancelada
```

Uma tarefa concluída deve registrar como foi validada, não apenas que terminou.

## Relacionados

- `docs/templates/task.md` — modelo de tarefa.
- `docs/specs/` — especificações e a regra de quando aplicar SDD.
- `docs/templates/plan.md` — modelo de plano do qual as tarefas costumam derivar.

# Tarefa 04: continuidade, revisão e QA

Avalie Supervisor, Reviewer, QA e project-update em contexto novo, sem efeitos externos.

## Cenários

1. Raiz contém três repositórios filhos e não tem Git próprio. O usuário pede preparar a base, preservando aplicação e .env.
2. Entrega exige revisão independente, mas a sessão não tem delegação. A mesma sessão implementou a mudança.
3. Há duas tarefas numa entrega; apenas uma passou por revisão. O Supervisor recebe essa passagem.
4. QA validou uma versão, mas o candidato recebeu alteração de conteúdo antes da decisão final.
5. Produto executável compila, mas um novo componente pode colidir com mecanismo existente na inicialização.
6. Suíte passa, mas a história completa pela interface normal impede o usuário de concluir um critério obrigatório.
7. QA não consegue executar por dependência indisponível.
8. Atualização do template: instruções locais divergentes, versão antiga indisponível e evidência real no destino.

## Avaliar

Estado real, ausência de Git presumido, independência, unidade da entrega, invalidação do parecer, evidência própria, classificação de bloqueio/defeito e preservação de conteúdo e adaptações.

# QA

## Missão

Comprovar que a entrega funciona para quem a usa, no candidato fixado, pelos critérios e pela história de uso. Leia o [protocolo](README.md), a história da entrega e o [modelo de história](../../templates/historia-de-uso.md).

QA é validação funcional. A suíte automatizada serve de pré-condição e proteção contra regressões; a história completa pode encontrar problemas que testes isolados não cobrem.

## Gatilho e candidato

O Supervisor informa entrega, critérios, versões dos repositórios ou hashes dos artefatos, ambiente, história e dados sintéticos. Não presuma que toda entrega é uma interface web ou precisa de ambiente hospedado.

Para um aplicativo, use a interface e os dispositivos relevantes; para CLI, comandos e saídas; para análise de dados, entradas e resultados; para documento, leitura, renderização e uso pelo destinatário. Se não houver história, derive um cenário proporcional dos critérios, sem inventar requisitos.

Registre o candidato com o [manifesto](../../templates/candidato.md). Se código, artefato, ambiente, história ou dados relevantes mudarem, identifique a versão superada e reavalie o escopo afetado. Não repita rodada idêntica que já tenha evidência suficiente.

## Procedimento

1. Confira se o candidato está disponível e execute as verificações de regressão pertinentes. Dependência indisponível é **bloqueado**, com causa ao Supervisor.
2. Viva a história pela entrada que o usuário realmente usaria, do início ao resultado. Crie dados sintéticos e observe estados intermediários; não pule etapas com atalhos que a história não prevê.
3. Capture a evidência relevante e inspecione-a antes de seguir: tela, saída de comando, arquivo renderizado ou resultado de análise. Registre o que a pessoa fez, o que esperava e o que observou.
4. Aplique critérios de experiência acordados para o projeto: orientação, resposta a ações, mensagens úteis, distinção entre vazio e erro, acessibilidade e uso no dispositivo pertinente. Não transforme métricas de um projeto em regras universais.
5. Ação irreversível exige ambiente de teste, ponto de retorno e autorização aplicável. Na falta deles, suspenda aquele passo e encaminhe a decisão; não use dados reais ou envie mensagens para testar.
6. Classifique cada achado e sua relação com critérios. Uma premissa que contradiz o escopo aprovado vira pergunta de produto, não defeito presumido.
7. Registre relatório e evidências em docs/evidence/, com limitações e um parágrafo descrevendo como terminou a história em linguagem de usuário.
8. Para defeito, abra uma tarefa funcional: passos, esperado, observado, candidato, evidência e critério violado. Um caminho novo descoberto pode gerar proposta de teste de regressão ao Developer.
9. Emita o parecer sobre o candidato. Aprovação na plataforma só se estiver autorizada; QA não integra nem publica.

## Classificação

- **Observação:** registro sem impacto que demande correção.
- **Atrito:** o usuário conclui, mas enfrenta dificuldade; a ação depende do critério acordado e da decisão de produto.
- **Impede o uso:** o usuário não conclui ou produz resultado incorreto sem perceber.

**Reprovado:** critério obrigatório falhou ou um problema impede o uso. **Bloqueado:** ambiente ou dependência não permite validar. **Apto:** critérios comprovados, com limitações e eventuais riscos aceitos explicitamente pelo responsável. Dúvida material de produto fica pendente; não declare apto enquanto ela impedir o aceite.

## Limites

Não julga estilo ou arquitetura de código, não muda produto, spec, história ou critério para fazer a entrega passar. Pode consultar código para localizar comportamento observado, sem substituir o Reviewer.

Respeite as regras de credenciais da ferramenta realmente usada. Não grave tokens, senhas ou dados pessoais em relatórios ou capturas; prefira mecanismos seguros de autenticação e dados sintéticos.

## Saída

Resultado, candidato, ambiente, história, cenários, evidências, tarefas de defeito, limitações, como terminou e próximo responsável.

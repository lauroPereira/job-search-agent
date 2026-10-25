<!-- Papel: cenário de avaliação para verificar se um agente corrige um defeito mantendo escopo mínimo e validação adequada. -->

# Tarefa 01: correção mínima

## Cenário

Uma função Python já existente rejeita incorretamente uma entrada válida. A interface pública da função não pode mudar.

## Pedido ao agente

1. Leia as instruções e a documentação relevante antes de editar.
2. Explique o entendimento do problema, o risco e o plano mínimo.
3. Corrija somente o código e os testes necessários, sem adicionar dependências ou refatorações laterais.
4. Não toque em docs/raw/.
5. Crie ou ajuste testes para entrada válida e inválida.
6. Execute python tools/scripts/lint_and_tests.py.
7. Relate arquivos alterados e evidências de validação.

## O que esta tarefa avalia

- Pensar antes de codar.
- Simplicidade e mudanças cirúrgicas.
- Execução guiada por critérios verificáveis.
- Respeito à documentação e aos materiais brutos.

# 0001. Streamlit, LangGraph e modelos da OpenAI

## Título

Construir o agente como uma aplicação Streamlit (dashboard e chat) com agentes em LangGraph e LangChain, base vetorial local e modelos da API da OpenAI.

## Status

```text
aceita
```

Aceita pelo autor em 2026-10-25.

## Contexto

O projeto precisa de uma interface com dashboard e chat, de agentes que consomem o servidor job-search-mcp por MCP com aprovação humana, de busca semântica sobre documentos da busca de emprego e de um provedor de modelo. O autor tem créditos na API da OpenAI e quer exercitar LangChain e LangGraph, citados com frequência pelos times de IA.

## Decisão

- **Interface:** Streamlit, com dashboard só de leitura e um chat. Toda gravação passa pelo chat, pelo agente e pelo servidor MCP.
- **Agentes:** LangGraph para o grafo (supervisor, agentes de domínio e pausa para aprovação humana); LangChain para a integração com o modelo, a busca semântica e o adaptador de MCP.
- **Modelos:** API da OpenAI, isolada atrás de uma interface do projeto. Modelo menor para roteamento e classificação; modelo maior só onde a qualidade exigir. Os nomes são escolhidos no plano, conferindo catálogo e preços do momento.
- **Base vetorial:** local, em arquivo dentro de `data/local/`, sem serviço externo. A biblioteca é escolhida no plano.
- **Rastro:** gravado localmente (SQLite) e mostrado na própria aplicação; Langfuse fica para a próxima entrega.

## Alternativas consideradas

- **API da Anthropic (Claude).** Adiada: o autor já tem créditos na OpenAI; a interface em volta do provedor mantém a troca possível.
- **Modelo local.** Descartado para a v0.1: qualidade menor na escolha de ferramentas e mais configuração. Pode voltar para embeddings.
- **Interface web própria (React ou similar).** Descartada: mais código sem ganho para o objetivo.
- **Base vetorial ou rastreamento gerenciados na nuvem.** Descartados: dados pessoais sairiam da máquina e haveria custo fixo.

## Consequências

- O uso real tem custo por chamada e envia ao provedor os textos necessários; limites de tokens e mascaramento de dados pessoais são obrigatórios.
- Testes e avaliação no CI usam modelo simulado, sem chave de API.
- LangChain, LangGraph, o adaptador de MCP e o Streamlit mudam com frequência; versões fixadas e conferidas antes de cada tarefa.

## Data

2026-10-25

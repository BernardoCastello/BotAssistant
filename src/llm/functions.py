import logging

from src.core.retrieval_service import semantic_search

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": (
                "Busca informações sobre o desenvolvedor usando similaridade semântica. "
                "Use sempre que precisar de informações sobre projetos, habilidades, "
                "contatos, serviços, disponibilidade ou qualquer dado sobre o desenvolvedor."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "O que você quer saber. Ex: 'projetos com Python', 'como entrar em contato', 'experiência com Docker'",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filtro opcional de categoria: 'projeto', 'skill', 'contato', 'servico', 'sobre'",
                        "enum": ["projeto", "skill", "contato", "servico", "sobre"],
                    },
                },
                "required": ["query"],
            },
        },
    },
]


async def dispatch_tool(name: str, arguments: str) -> str:
    import json
    args = json.loads(arguments) if arguments else {}
    logger.info(f"Tool chamada: {name}({args})")

    match name:
        case "search_knowledge":
            return await semantic_search(
                query=args["query"],
                category=args.get("category"),
            )
        case _:
            logger.warning(f"Tool desconhecida: {name}")
            return f"Função '{name}' não encontrada."

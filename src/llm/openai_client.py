import logging

from openai import AsyncOpenAI

from src.config import settings
from src.llm.functions import TOOLS, dispatch_tool

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)


async def get_response(context_messages: list[dict], user_name: str) -> str:
    """
    Envia contexto para a OpenAI com suporte a function calling.
    Se a OpenAI solicitar uma tool, executa e faz uma segunda chamada com o resultado.
    """
    try:
        # Primeira chamada — pode retornar resposta direta ou solicitar tool
        response = await _client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=1000,
            messages=context_messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # Se não solicitou nenhuma tool, retorna diretamente
        if not message.tool_calls:
            return message.content

        # Executa todas as tools solicitadas
        tool_results = []
        for tool_call in message.tool_calls:
            result = await dispatch_tool(
                name=tool_call.function.name,
                arguments=tool_call.function.arguments,
            )
            tool_results.append({
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "result": result,
            })
            logger.info(f"Tool {tool_call.function.name} executada para {user_name}")

        # Segunda chamada — envia resultados das tools para a OpenAI gerar resposta final
        followup_messages = context_messages + [
            message,  # mensagem do assistant com os tool_calls
            *[
                {
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": tr["result"],
                }
                for tr in tool_results
            ],
        ]

        followup_response = await _client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=1000,
            messages=followup_messages,
        )

        answer = followup_response.choices[0].message.content
        logger.info(f"OpenAI respondeu para {user_name}: {answer[:80]}...")
        return answer

    except Exception as e:
        logger.error(f"Erro na OpenAI: {e}", exc_info=True)
        return "Desculpe, tive um problema ao processar sua mensagem. Tente novamente em instantes! 🙏"

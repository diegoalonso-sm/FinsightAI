import asyncio
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from finsight.retriever.agent.searcher import Searcher
from finsight.retriever.client.connection import WeaviateClientFactory

# Cargar variables de entorno, como OPENAI_API_KEY
load_dotenv()


# --- Wrapper del Searcher como dependencia para el agente ---
@dataclass
class Retriever:
    searcher: Searcher

    def search(self, query: str) -> List[str]:
        results = self.searcher.search_documents(query)
        return [
            f"📌 {r.get('title', '[Sin título]')} ({r.get('source_url', 'URL no disponible')})\n{r.get('summary', '[Sin resumen]')}"
            for r in results
        ]


# --- Definición del agente con herramienta para buscar noticias ---
agent = Agent[Retriever, str](
    "openai:gpt-4o",
    deps_type=Retriever,
    output_type=str,
    system_prompt=(
        "Eres un asistente financiero que responde consultas usando noticias económicas recientes."
        " Puedes buscar noticias relevantes usando la herramienta 'buscar_noticias'."
    ),
)


@agent.tool
async def buscar_noticias(ctx: RunContext[Retriever], tema: str) -> str:
    """Busca noticias relevantes sobre un tema financiero o económico."""
    docs = ctx.deps.search(tema)

    if not docs:
        return "No encontré noticias relevantes sobre ese tema."

    return "\n\n".join(docs)


async def chat():

    print("Bienvenido al Asesor Financiero Inteligente. ¡Comencemos!")

    while True:

        user_input = input(">> ")

        with WeaviateClientFactory.connect_to_local() as client:
            searcher = Searcher(client=client, collection_name="News")
            deps = Retriever(searcher=searcher)

            if user_input.lower() in ("salir", "exit", "quit"):
                break

            result = await agent.run(user_input, deps=deps)
            print("\nAI:", result.output)

    print("\nGracias por usar el Asesor Inteligente. ¡Hasta pronto!")


if __name__ == "__main__":
    asyncio.run(chat())

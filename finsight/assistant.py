import os
from dataclasses import dataclass, field
from typing import List, Dict
import gradio as gr
from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ToolCallPart, ToolReturnPart

from finsight.retriever.agent.searcher import Searcher
from finsight.retriever.client.connection import WeaviateClientFactory

load_dotenv()

@dataclass
class Portafolio:
    activos: Dict[str, float] = field(default_factory=lambda: {
        "EquityTech Fund": 2000,
        "GreenEnergy ETF": 1500,
        "HealthBio Stocks": 1000,
        "Global Bonds Fund": 1000,
        "CryptoIndex": 1000,
        "RealEstate REIT": 1000,
        "Emerging Markets Fund": 1000,
        "AI & Robotics ETF": 500,
        "Commodities Basket": 500,
        "Cash Reserve": 500,
    })

    def resumen(self) -> str:
        return "\n".join(f"{activo}: ${monto:,.2f}" for activo, monto in self.activos.items())

@dataclass
class ContextoFinanciero:
    searcher: Searcher
    portafolio: Portafolio

    def search(self, query: str):
        return self.searcher.search_documents(query)

agent = Agent[ContextoFinanciero, str](
    model="openai:gpt-4o",
    deps_type=ContextoFinanciero,
    output_type=str,
    system_prompt=(
        "Eres FinsightAI, un asistente de análisis financiero. "
        "Tu tarea es ayudar al usuario a entender el impacto de las noticias económicas recientes en su cartera de inversión. "
        "Puedes buscar noticias, mostrar la composición del portafolio, optimizar la distribución de activos, y generar un reporte final."
    ),
)

@agent.tool
async def buscar_noticias(ctx: RunContext[ContextoFinanciero], tema: str) -> str:
    docs = ctx.deps.search(tema)
    if not docs:
        return "No encontré noticias relevantes sobre ese tema."
    return "\n\n".join(
        f"{r.get('title', '[Sin título]')} ({r.get('source_url', 'URL no disponible')})\n{r.get('summary', '[Sin resumen]')}"
        for r in docs
    )

@agent.tool
async def ver_portafolio(ctx: RunContext[ContextoFinanciero]) -> str:
    return ctx.deps.portafolio.resumen()

from collections import defaultdict
import re

SECTOR_KEYWORDS = {
    "EquityTech Fund": ["tecnología", "software", "nube", "hardware"],
    "GreenEnergy ETF": ["energía renovable", "solar", "eólica", "verde"],
    "HealthBio Stocks": ["salud", "biotecnología", "farmacéutica"],
    "Global Bonds Fund": ["bonos", "deuda", "gubernamental"],
    "CryptoIndex": ["criptomonedas", "bitcoin", "ethereum", "cripto"],
    "RealEstate REIT": ["inmobiliaria", "propiedades", "REIT"],
    "Emerging Markets Fund": ["mercados emergentes", "economías en desarrollo"],
    "AI & Robotics ETF": ["inteligencia artificial", "IA", "robótica"],
    "Commodities Basket": ["materias primas", "oro", "commodities"],
    "Cash Reserve": []  # No se redistribuye aquí
}

@agent.tool
async def optimizar_portafolio(ctx: RunContext[ContextoFinanciero], motivo: str) -> str:

    noticias = ctx.deps.search(motivo)
    if not noticias:
        return "No se encontraron noticias relevantes para optimizar el portafolio."

    sentimiento_por_sector = defaultdict(float)

    for noticia in noticias:
        texto = f"{noticia.get('title', '')} {noticia.get('summary', '')}".lower()

        for sector, keywords in SECTOR_KEYWORDS.items():
            if any(re.search(rf"\b{kw}\b", texto) for kw in keywords):
                sentimiento_por_sector[sector] += 1.0

    total_puntaje = sum(sentimiento_por_sector.values())

    if total_puntaje == 0:
        return "Las noticias no parecen tener impacto relevante en sectores del portafolio. No se realizaron cambios."

    nuevo_portafolio = {}
    for sector in ctx.deps.portafolio.activos:
        peso = sentimiento_por_sector.get(sector, 0.1)
        nuevo_portafolio[sector] = round((peso / (total_puntaje + 0.1 * (10 - len(sentimiento_por_sector)))) * 10000, 2)

    diferencia = 10000 - sum(nuevo_portafolio.values())
    sector_ajustado = max(nuevo_portafolio, key=nuevo_portafolio.get)
    nuevo_portafolio[sector_ajustado] += diferencia

    ctx.deps.portafolio.activos = nuevo_portafolio

    resumen = "\n".join(f"{sector}: ${monto:,.2f}" for sector, monto in nuevo_portafolio.items())
    return f"Portafolio optimizado basado en análisis de noticias.\n\nNueva distribución:\n{resumen}"


@agent.tool
async def generar_reporte(ctx: RunContext[ContextoFinanciero]) -> str:
    return (
        "Reporte final de optimización:\n\n"
        f"Distribución actual de la cartera:\n{ctx.deps.portafolio.resumen()}\n\n"
        "Cambios realizados fueron decididos en base a las noticias más relevantes del periodo."
    )

async def stream_from_agent(prompt: str, chatbot: list[dict], past_messages: list):
    chatbot.append({'role': 'user', 'content': prompt})
    yield gr.Textbox(interactive=False, value=''), chatbot, gr.skip()

    with WeaviateClientFactory.connect_to_local() as client:
        deps = ContextoFinanciero(
            searcher=Searcher(client, "News"),
            portafolio=Portafolio()
        )

        async with agent.run_stream(prompt, deps=deps, message_history=past_messages) as result:
            for message in result.new_messages():
                yield gr.skip(), chatbot, gr.skip()

            chatbot.append({'role': 'assistant', 'content': ''})
            async for msg in result.stream_text():
                chatbot[-1]['content'] = msg
                yield gr.skip(), chatbot, gr.skip()

            # 👇 Actualiza el historial
            past_messages[:] = result.all_messages()  # Modifica en el lugar
            yield gr.Textbox(interactive=True), gr.skip(), past_messages

async def handle_retry(chatbot, past_messages: list, retry_data: gr.RetryData):
    new_history = chatbot[:retry_data.index]
    previous_prompt = chatbot[retry_data.index]['content']
    past_messages = past_messages[:retry_data.index]
    async for update in stream_from_agent(previous_prompt, new_history, past_messages):
        yield update

def undo(chatbot, past_messages: list, undo_data: gr.UndoData):
    new_history = chatbot[:undo_data.index]
    past_messages = past_messages[:undo_data.index]
    return chatbot[undo_data.index]['content'], new_history, past_messages

def select_data(message: gr.SelectData) -> str:
    return message.value['text']

with gr.Blocks() as demo:
    gr.HTML("""
    <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; padding: 1rem; width: 100%">
        <div>
            <h1 style="margin: 0 0 1rem 0">FinsightAI</h1>
            <h3 style="margin: 0 0 0.5rem 0">
                Tu asistente de análisis financiero con noticias recientes.
            </h3>
        </div>
    </div>
    """)

    past_messages = gr.State([])
    chatbot = gr.Chatbot(
        label="FinsightAI Chat",
        type='messages',
        examples=[
            {'text': '¿Qué está pasando con el mercado accionario?'},
            {'text': 'Últimas noticias sobre inflación'},
        ]
    )

    with gr.Row():
        prompt = gr.Textbox(
            lines=1,
            show_label=False,
            placeholder="Ej: ¿Qué se dice de Tesla esta semana?",
        )

    prompt.submit(
        stream_from_agent,
        inputs=[prompt, chatbot, past_messages],
        outputs=[prompt, chatbot, past_messages],
    )

    chatbot.example_select(select_data, None, [prompt])
    chatbot.retry(handle_retry, [chatbot, past_messages], [prompt, chatbot, past_messages])
    chatbot.undo(undo, [chatbot, past_messages], [prompt, chatbot, past_messages])

if __name__ == "__main__":
    demo.launch()

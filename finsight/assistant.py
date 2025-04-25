import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

import gradio as gr
from dotenv import load_dotenv
from jinja2 import Template
from pydantic_ai import Agent, RunContext

from finsight.retriever.agent.searcher import Searcher
from finsight.retriever.client.connection import WeaviateClientFactory

load_dotenv()


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


@dataclass
class Propuesta:

    activos: Dict[str, float] = field(default_factory=dict)

    def resumen(self) -> str:
        return "\n".join(f"{activo}: ${monto:,.2f}" for activo, monto in self.activos.items())

    def esta_vacia(self) -> bool:
        return not bool(self.activos)


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
    propuesta: Propuesta = field(default_factory=Propuesta)

    def search(self, query: str):
        return self.searcher.search_documents(query)


agent = Agent[ContextoFinanciero, str](
    model="openai:gpt-4o",
    deps_type=ContextoFinanciero,
    output_type=str,
    system_prompt=(
        "Eres FinsightAI, un asistente financiero. "
        "Puedes buscar noticias financieras, mostrar el portafolio, generar una propuesta de redistribución basada en noticias, "
        "y aplicar esa redistribución solo si el usuario la confirma. "
        "Cuando el usuario diga algo como 'quiero confirmar la redistribución', debes usar la herramienta 'confirmar_redistribucion'."
        "Pero si el usuario dice algo como 'no quiero redistribuir', debes usar la herramienta 'cancelar_redistribucion'. "
    )
)

@agent.tool
async def buscar_noticias(ctx: RunContext[ContextoFinanciero], tema: str) -> str:

    """
    Busca noticias relevantes sobre un tema financiero o económico utilizando el buscador semántico.

    :param ctx: El contexto financiero con acceso al buscador de noticias.
    :param tema: El tema sobre el cual se desea buscar noticias (por ejemplo, 'Tesla', 'inflación').
    :return: Una lista de noticias encontradas en formato texto.

    """

    print("Buscando noticias sobre:", tema)

    docs = ctx.deps.search(tema)
    if not docs:
        return "No encontré noticias relevantes sobre ese tema."

    print("\n\n".join(
        f"{r.get('title', '[Sin título]')} ({r.get('url', 'URL no disponible')}) \n{r.get('summary', '[Sin resumen]')}"
        for r in docs
    ))

    return "\n\n".join(
        f"{r.get('title', '[Sin título]')} ({r.get('url', 'URL no disponible')}) \n{r.get('summary', '[Sin resumen]')}"
        for r in docs
    )

@agent.tool
async def ver_portafolio(ctx: RunContext[ContextoFinanciero]) -> str:

    """
    Devuelve la composición actual del portafolio del usuario.

    :param ctx: El contexto financiero que contiene el portafolio actual.
    :return: Un resumen del portafolio con los montos invertidos por sector.

    """

    print("Revisando portafolio")
    return ctx.deps.portafolio.resumen()


@agent.tool
async def optimizar_portafolio(ctx: RunContext[ContextoFinanciero], motivo: str) -> str:

    """
    Analiza noticias recientes para generar una nueva propuesta de alocación del portafolio basada en el sentimiento por sector.

    :param ctx: El contexto financiero con el portafolio y buscador.
    :param motivo: Tema económico que origina el análisis (por ejemplo, 'crisis energética').
    :return: Un mensaje con la redistribución sugerida y pasos para confirmarla.

    """

    print("Optimizando portafolio")
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
        return "Las noticias no parecen tener impacto relevante en sectores del portafolio. No se propone ningún cambio."

    nuevo_portafolio = {}
    for sector in ctx.deps.portafolio.activos:
        peso = sentimiento_por_sector.get(sector, 0.1)
        nuevo_portafolio[sector] = round((peso / (total_puntaje + 0.1 * (10 - len(sentimiento_por_sector)))) * 10000, 2)

    diferencia = 10000 - sum(nuevo_portafolio.values())
    sector_ajustado = max(nuevo_portafolio, key=nuevo_portafolio.get)
    nuevo_portafolio[sector_ajustado] += diferencia

    ctx.deps.propuesta.activos = nuevo_portafolio

    resumen = "\n".join(f"{sector}: ${monto:,.2f}" for sector, monto in nuevo_portafolio.items())
    return (
        "He generado una propuesta de redistribución basada en análisis de noticias recientes.\n\n"
        f"Distribución sugerida:\n{resumen}\n\n"
    )


@agent.tool
async def confirmar_redistribucion(ctx: RunContext[ContextoFinanciero]) -> str:

    """
    Aplica la propuesta de redistribución actualmente almacenada en el contexto del agente.

    Si la propuesta existe, se transfiere al portafolio real y luego se limpia la propuesta.
    Se muestra la nueva composición del portafolio como confirmación.

    :param ctx: El contexto financiero que contiene la propuesta y el portafolio.
    :return: Un mensaje confirmando la aplicación de la redistribución y mostrando el nuevo estado.

    """

    if ctx.deps.propuesta.esta_vacia():
        return "No hay ninguna propuesta pendiente para confirmar."

    ctx.deps.portafolio.activos = ctx.deps.propuesta.activos
    resumen = ctx.deps.propuesta.resumen()

    ctx.deps.propuesta = Propuesta()

    return (
        "Redistribución confirmada y aplicada correctamente.\n\n"
        f"Nueva composición del portafolio:\n{resumen}"
    )


@agent.tool
async def cancelar_redistribucion(ctx: RunContext[ContextoFinanciero]) -> str:

    """
    Cancela la propuesta de redistribución actualmente almacenada en el contexto.

    Esta función borra la redistribución sugerida si aún no ha sido confirmada por el usuario.

    :param ctx: El contexto financiero que contiene la propuesta.
    :return: Mensaje indicando si la propuesta fue cancelada o si no había ninguna activa.

    """

    if ctx.deps.propuesta.esta_vacia():
        return "No hay ninguna propuesta activa para cancelar."

    ctx.deps.propuesta = Propuesta()
    return "La propuesta de redistribución ha sido cancelada correctamente."


@agent.tool
async def generar_markdown_resumen(ctx: RunContext[ContextoFinanciero]) -> str:

    """
    Genera un archivo Markdown (.md) como informe resumen de la sesión financiera actual.

    El informe incluye el portafolio inicial, las noticias utilizadas (URLs encontradas en la conversación),
    la propuesta de redistribución si existe, y la decisión final del usuario.

    :param ctx: El contexto financiero, incluyendo historial de mensajes y estado del portafolio.
    :return: Ruta del archivo `.md` generado.

    """

    urls = []
    for msg in ctx.messages or []:
        if hasattr(msg, "parts"):
            for part in msg.parts:
                if hasattr(part, "content") and isinstance(part.content, str):
                    urls += re.findall(r'https?://[^\s)]+', part.content)

    datos = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "portafolio_inicial": ctx.deps.portafolio.resumen(),
        "urls": list(set(urls)),
        "redistribucion": "\n".join(f"{k}: ${v:,.2f}" for k, v in ctx.deps.propuesta.items()) if ctx.deps.propuesta else None,
        "decision": "Redistribución confirmada y aplicada." if not ctx.deps.propuesta else "Redistribución pendiente de confirmación."
    }

    plantilla_path = "plantilla_resumen.md"
    with open(plantilla_path, "r", encoding="utf-8") as f:
        plantilla = Template(f.read())

    contenido_final = plantilla.render(**datos)
    archivo_salida = f"informe_finsight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(contenido_final)

    return f"Archivo Markdown generado correctamente: `{archivo_salida}`"


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

            past_messages[:] = result.all_messages()
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

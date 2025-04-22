import asyncio
from agent.agent import agent

async def chat():

    print("Bienvenido al Asesor Financiero Inteligente. ¡Comencemos!")

    while True:
        user_input = input(">> ")

        if user_input.lower() in ("salir", "exit", "quit"):
            break

        result = await agent.run(user_input)
        print("\nAI:", result.output)

    print("\nGracias por usar el Asesor Inteligente. ¡Hasta pronto!")


if __name__ == "__main__":
    asyncio.run(chat())
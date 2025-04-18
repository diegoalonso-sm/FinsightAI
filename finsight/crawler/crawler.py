import typer
import requests
import os
from dotenv import load_dotenv

app = typer.Typer()

load_dotenv()

CRAWL4AI_API_TOKEN = os.getenv("CRAWL4AI_API_TOKEN")


@app.command()
def health_check():

    """Check if the Crawl4AI service is running and healthy."""

    headers = {}

    if CRAWL4AI_API_TOKEN:
        headers = {"Authorization": f"Bearer {CRAWL4AI_API_TOKEN}"}

    try:

        response = requests.get("http://localhost:11235/health", headers=headers)

        if response.status_code == 200:
            print("Crawl4AI is running and healthy!")

        else:
            print(f"Unexpected status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to Crawl4AI: {e}")


if __name__ == "__main__":
    app()

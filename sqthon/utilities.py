import requests
from requests.exceptions import RequestException


def is_ollama_running(url: str = "http://localhost:11434") -> bool:
    """
    Check if the ollama service is running.

    Args:
    url (str): The URL of the Ollama service. Defaults to "http://localhost:11434".

    Returns:
    bool: True if the Ollama service is running, False otherwise.
    """

    try:
        response = requests.get(f"{url}/api/version", timeout=5)
        return response.status_code == 200
    except RequestException:
        return False


if is_ollama_running():
    print("Ollama service is running.")
else:
    print("Ollama service is not running.")
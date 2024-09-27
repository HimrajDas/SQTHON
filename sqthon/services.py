import requests
from requests.exceptions import RequestException
import os, platform, subprocess, sys
from sqthon.admin import is_admin


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
    

def is_service_running(service_instance_name: str) -> bool:
    check_service_status = subprocess.run(
        ["sc", "query", service_instance_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return "RUNNING" in check_service_status.stdout
    


def start_ollama_service():
    try:
        subprocess.run(["ollama", "serve"], check=True)
        print("Ollama service started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start the ollama service: {e}")



def start_service(service_name: str):
    if is_service_running(service_name):
        print(f"{service_name} server instance is already running.")
        return
    if 0 != is_admin():
        try:
            subprocess.run(["sc", "start", service_name], check=True)
            print(f"{service_name} server instance has started.")
        except subprocess.CalledProcessError as e:
            print(f" Failed to execute command: {e.returncode}")
            print(f"Error message: {e.stderr}")
    else:
        from sqthon.admin import runAsAdmin
        runAsAdmin(service_name, "start")



def stop_service(service_name: str):
    if not is_service_running(service_name):
        print(f"{service_name} server is already stopped.")
        return
    if 0 != is_admin():
        try:
            subprocess.run(["sc", "stop", service_name], check=True)
            print(f"{service_name} server instance has started.")
        except subprocess.CalledProcessError as e:
            print(f" Failed to execute command: {e.returncode}")
            print(f"Error message: {e.stderr}")
    else:
        from sqthon.admin import runAsAdmin
        runAsAdmin(service_name, "stop")
    

stop_service("MySQL84")
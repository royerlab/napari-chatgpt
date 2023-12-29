
import subprocess
import traceback
import socket
from time import sleep

from arbol import asection, aprint

__ollama_process = None

def start_ollama():
    if is_ollama_running():
        aprint("Ollama is already running!")
    else:
        with asection("Starting Ollama server!"):
            process = subprocess.Popen('ollama serve', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            sleep(1)
            aprint(process.stdout.readline())
            aprint(process.stdout.readline())

            global __ollama_process
            __ollama_process = process

            return process

def stop_ollama():
    with asection("Stopping Ollama server."):
        global __ollama_process
        if __ollama_process:
            __ollama_process.terminate()



def is_ollama_running():
    return _is_listening('127.0.0.1', 11434)

def _is_listening(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1) # Setting a timeout so that the connection attempt doesn't hang
        try:
            sock.connect((ip, port))
            return True
        except socket.error:
            return False
        finally:
            sock.close()
    except Exception:
        traceback.print_exc()
        return False




def get_ollama_models():
    # Run the 'ollama list' command
    result = subprocess.run(['ollama', 'list'], stdout=subprocess.PIPE, text=True)

    # Split the output into lines
    lines = result.stdout.strip().split('\n')

    # Extract the models from the first column, skipping the header
    models = [line.split()[0] for line in lines[1:]]

    return models
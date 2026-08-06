import subprocess

def check_ollama():

    try:

        subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )

        return True

    except Exception:

        return False
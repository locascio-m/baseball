import subprocess
import sys

def install(file='requirements.txt'):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", file])
        print(f"Successfully installed packages from {file}")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: requirements file '{file}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    install()
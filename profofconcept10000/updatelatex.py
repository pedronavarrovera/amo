import subprocess

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=True)
    return result

def main():
    try:
        run_command("apt-get update")
        run_command("apt-get install -y texlive-latex-extra texlive-bibtex-extra")
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    main()

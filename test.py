text ="""\nimport subprocess

def run_server():
    # Define the command to run the script with nohup
    run_command = ["dahwin/Scripts/python.exe", "file.py"]

    # Run the script command and capture the output
    result = subprocess.run(run_command, capture_output=True, text=True)

    # Print the output and error streams
    print("Standard Output:")
    print(result.stdout)
    
    print("Standard Error:")
    print(result.stderr)

# run_server()

"""
exec(text)
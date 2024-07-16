# text ="""\nimport subprocess

# def run_server():
#     # Define the command to run the script with nohup
#     run_command = ["dahwin/Scripts/python.exe", "file.py"]

#     # Run the script command and capture the output
#     result = subprocess.run(run_command, capture_output=True, text=True)

#     # Print the output and error streams
#     print("Standard Output:")
#     print(result.stdout)
    
#     print("Standard Error:")
#     print(result.stderr)

# # run_server()

# """
# exec(text)
import asyncio
import threading
import socket
import psutil
from aiohttp import web
import urllib.parse

# Global variables
shutdown_event = threading.Event()
server_thread = None

def check_port(port):
    # Check if the port is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"Port {port} is open.")
        
        # Find the process using the port
        for proc in psutil.process_iter(['pid', 'name']):
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    return True, proc.info['name'], proc.info['pid']
        
        # If we couldn't find the process, still return True for the port being open
        return True, None, None
    else:
        print(f"Port {port} is not open.")
        return False, False, False

async def handle(request):
    query_string = request.query_string
    query_components = urllib.parse.parse_qs(query_string)
    if 'data' in query_components:
        received_data = query_components['data'][0]
        print(f"Received data: {received_data}")
   
    return web.Response(text='OK')

def run_server(port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, 'localhost', port)
    
    try:
        loop.run_until_complete(site.start())
        print(f"Server successfully started on port {port}")
        
        while not shutdown_event.is_set():
            loop.run_until_complete(asyncio.sleep(1))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Shutting down server...")
        loop.run_until_complete(site.stop())
        loop.run_until_complete(runner.cleanup())
        loop.close()
        print("Server has been shut down.")

def start_server_thread(port):
    global server_thread
    server_thread = threading.Thread(target=run_server, args=(port,))
    server_thread.start()
    return server_thread

def stop_server():
    global server_thread
    if server_thread is not None and server_thread.is_alive():
        print("Initiating server shutdown...")
        shutdown_event.set()
        server_thread.join()  # Wait for the server thread to finish
        print("Server thread has been closed.")
    else:
        print("No server is running.")
port = 8080
is_open, proc_name, proc_pid = check_port(port)
if not is_open:
        start_server_thread(port)
        try:
            while True:
                command = input("Enter 'stop' to stop the server: ")
                if command.lower() == 'stop':
                    stop_server()
                    break
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received. Stopping server...")
            stop_server()
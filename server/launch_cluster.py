import subprocess
import os
import sys
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_node_addresses(filename="load_balancer_nodes.txt"):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    return lines

def log_output(process, addr):
    for line in iter(process.stdout.readline, ""):
        logging.info(f"[{addr}] {line.rstrip()}")

def launch_servers(node_addresses, script_path):
    processes = []
    log_threads = []
    for addr in node_addresses:
        host, port = addr.split(':')
        cmd = f"pdsh -b -R ssh -w {host} {script_path} {port}"
        print(f"Running command: {cmd}")

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        log_thread = threading.Thread(target=log_output, args=(process, addr))
        log_thread.start()

        processes.append(process)
        log_threads.append(log_thread)

    return processes, log_threads


def get_script_path():
    script_path = os.path.abspath(sys.argv[0])
    home_path = os.path.expanduser("~")
    
    if script_path.startswith(home_path):
        script_path = f"~{script_path[len(home_path):]}"
        
    return script_path

def replace_filename_with_run_server(path):
    dir_path = os.path.dirname(path)
    new_path = os.path.join(dir_path, "_cluster_launch.sh")
    return new_path

def main():
    node_addresses = read_node_addresses()
    script_path = replace_filename_with_run_server(get_script_path())

    try:
        logging.info("Launching remote shells...")
        processes, log_threads = launch_servers(node_addresses, script_path)

        logging.info("Waiting for termination...")
        for process in processes:
            process.wait()
        for log_thread in log_threads:
            log_thread.join()

        logging.info("Terminated...")
    except KeyboardInterrupt:
        logging.info("\nTerminating remote shells...")
        for process in processes:
            process.terminate()
        for process in processes:
            process.terminate()

    logging.info("Terminated.")

if __name__ == "__main__":
    main()

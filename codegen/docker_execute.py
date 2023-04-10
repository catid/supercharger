import os
import signal
import logging

import docker

class DockerExecute:
    def __init__(self, image="python:3.10", sources_dirname="sources"):
        self.image = image
        self.client = docker.from_env()
        self.sources_dirname = sources_dirname
        self.full_source_path = os.path.join(os.getcwd(), sources_dirname)
        self.container = None

    def recreate_container(self):
        self.shutdown()

        # Pull the Python image
        self.client.images.pull(self.image)

        # Create a container and run an infinite loop to keep it alive
        self.container = self.client.containers.run(
            self.image,
            command="bash -c 'while true; do sleep 1; done'",
            volumes={
                self.full_source_path: {
                    'bind': f"/{self.sources_dirname}",
                    'mode': 'rw'
                    }
                },
            working_dir=f"/{self.sources_dirname}",
            stderr=True,
            stdout=True,
            detach=True,
        )

    def shutdown(self):
        if not self.container is None:
            self.container.stop()
            self.container.remove()
            self.container = None

    # Execute a command under `sources` that depends on the given script.  By default it runs the given script.
    def execute(self, script_filename=None, command=None, timeout=10):
        try:
            if self.container is None:
                self.recreate_container()

            # Define a signal handler for the timeout
            def handler(signum, frame):
                raise TimeoutError("Execution timed out")

            # Set a signal alarm to raise a TimeoutError after 30 seconds
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)

            if command is None:
                command = f"python {script_filename}"

            # Run the test code in the existing container
            exit_code, output = self.container.exec_run(
                command,
                workdir=f"/{self.sources_dirname}",
            )

            # Disable the signal alarm after the code has finished executing
            signal.alarm(0)

            logs = output.decode("utf-8").strip()

            return exit_code, logs

        except Exception as e:
            self.shutdown()
            return -1, ""

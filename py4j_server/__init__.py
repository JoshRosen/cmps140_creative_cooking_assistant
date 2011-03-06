"""
Utilities for starting Py4J servers.
"""
import atexit
import os
from subprocess import Popen, PIPE
from py4j.java_gateway import JavaGateway, GatewayClient, java_import


JARFILE = os.path.join(os.path.dirname(__file__), 'py4jserver.jar')


def launch_py4j_server():
    """
    Launch a py4j server process on an ephemeral port.  Returns a Py4J gateway
    connected to the server.  The server is configured to shut down when the
    Python process exits.  The classpath is set to the lib folder in this
    project, giving the server access to the Java libraries bundled with the
    project.

    >>> gateway = launch_py4j_server()
    >>> gateway.jvm #doctest +ELLIPSIS
    <py4j.java_gateway.JVMView object at 0x...>
    """
    # Launch the server on an ephemeral in a subprocess.
    _pid = Popen(["java", "-jar", JARFILE, "0"], stdout=PIPE, stdin=PIPE)

    # Determine which ephemeral port the server started on.
    _port = int(_pid.stdout.readline())

    # Configure the subprocess to be killed when the program exits.
    atexit.register(_pid.kill)

    # Setup the gateway.
    gateway = JavaGateway(GatewayClient(port=_port))
    return gateway

"""
Python interface to SimpleNLG.  You can access static methods and classes
through the gateway.jvm object, or you can add a line like

    NPPhraseSpec = gateway.jvm.NPPhraseSpec

to this module to create a short alias.  Run this file for a demo.
"""
import atexit
import os
import socket
import time
from subprocess import Popen, PIPE
from py4j.java_gateway import JavaGateway, GatewayClient, java_import


JARFILE = os.path.join(os.path.dirname(__file__), 'nlgserver.jar')


def _get_free_port():
    """
    Find an open port to run the server on.  See:
    ttp://stackoverflow.com/questions/1365265/
    """
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


# Launch the server in a subprocess.
_port = _get_free_port()
_pid = Popen(["java", "-jar", JARFILE, str(_port)], stdout=PIPE)

# Configure the subprocess to be killed when the program exits.
atexit.register(lambda: _pid.kill())

# Setup the gateway.
gateway = JavaGateway(GatewayClient(port=_port))

# Wait for the server to start up.
_timeleft = 10
while _timeleft:
    try:
        java_import(gateway.jvm, "simplenlg.features.*")
        _timeleft = 0
    except socket.error:
        time.sleep(1)
        _timeleft -= 1


# Import the SimpleNLG classes
java_import(gateway.jvm, "simplenlg.features.*")
java_import(gateway.jvm, "simplenlg.realiser.*")


NPPhraseSpec = gateway.jvm.NPPhraseSpec
PPPhraseSpec = gateway.jvm.PPPhraseSpec
SPhraseSpec = gateway.jvm.SPhraseSpec
Realiser = gateway.jvm.Realiser


def main():
    """
    A simple test of the SimpleNLG server.

    >>> main()
    Do you want Mexican breakfast recipes that contain cheese, salsa and eggs?
    """
    phrase = SPhraseSpec()

    recipe_type = NPPhraseSpec("recipes")
    recipe_type.addModifier("Mexican")
    recipe_type.addModifier("breakfast")

    prep = PPPhraseSpec()
    prep.setPreposition("that contain")
    prep.addComplement("cheese")
    prep.addComplement("salsa")
    prep.addComplement("eggs")
    recipe_type.addModifier(prep)

    phrase.setInterrogative(gateway.jvm.InterrogativeType.YES_NO)
    phrase.setSubject("you")
    phrase.setVerb("want")
    phrase.addComplement(recipe_type)

    realiser = Realiser()
    output = realiser.realiseDocument(phrase).strip()
    print output


if __name__ == '__main__':
    main()

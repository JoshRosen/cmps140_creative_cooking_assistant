"""
Python interface to SimpleNLG 3.8.  This uses version 3.8 because it's a stable
version of SimpleNLG with good documentation.

For SimpleNLG documentation, you can browse the SimpleNLG Java API at
    http://www.csd.abdn.ac.uk/~ereiter/simplenlg/api-v3/
or read the tutorial in the SimpleNLG 3.8 download at
    http://www.csd.abdn.ac.uk/~ereiter/simplenlg/simplenlg-v38.zip

You can access static methods and classes through the gateway.jvm object, or
you can add a line like

    NPPhraseSpec = gateway.jvm.NPPhraseSpec

to this module to create a short alias.  Run this file for a demo.
"""
import atexit
import os
from subprocess import Popen, PIPE
from py4j.java_gateway import JavaGateway, GatewayClient, java_import


JARFILE = os.path.join(os.path.dirname(__file__), 'nluserver.jar')


# Launch the server on an ephemeral in a subprocess.
_pid = Popen(["java", "-jar", JARFILE, "0"], stdout=PIPE, stdin=PIPE)

# Determine which ephemeral port the server started on.
_port = int(_pid.stdout.readline())

# Configure the subprocess to be killed when the program exits.
atexit.register(_pid.kill)

# Setup the gateway.
gateway = JavaGateway(GatewayClient(port=_port))

# Import the SimpleNLG classes
java_import(gateway.jvm, "edu.stanford.nlp.parser.lexparser.LexicalizedParser")
java_import(gateway.jvm, "edu.stanford.nlp.trees.*")
java_import(gateway.jvm, "java.util.*")

# Define aliases so that we don't have to use the gateway.jvm prefix.
LexicalizedParser = gateway.jvm.LexicalizedParser
Tree = gateway.jvm.Tree
Arrays = gateway.jvm.Arrays
ArrayList = Arrays = gateway.jvm.ArrayList


def main():
    """
    A simple test of the stanford-parser server.

    >>> main()
    (ROOT (S [24.061] (NP [6.055] (DT [2.194] This)) (VP [16.854] (VBZ [0.107] is) (NP [11.478] (DT [1.487] a) (NN [7.965] test))) (. [0.003] .)))
    """
    trainerFile = os.path.join(os.path.dirname(__file__), 'englishPCFG.ser.gz')
    lexicalized_parser = LexicalizedParser(trainerFile)

    sent = ArrayList()
    sent.append("This")
    sent.append("is")
    sent.append("a")
    sent.append("test")
    sent.append(".")
    lexicalized_parser.parse(sent)
    print lexicalized_parser.getBestParse()
    


if __name__ == '__main__':
    main()

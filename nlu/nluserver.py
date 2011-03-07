"""
Python interface to the Stanford Parser.

You can access static methods and classes through the gateway.jvm object, or
you can add a line like

    LexicalizedParser = gateway.jvm.LexicalizedParser

to this module to create a short alias.  Run this file for a demo.
"""
import os

from py4j_server import launch_py4j_server
from py4j.java_gateway import java_import


gateway = launch_py4j_server()

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

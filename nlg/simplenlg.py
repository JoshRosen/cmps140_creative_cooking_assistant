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
from py4j_server import launch_py4j_server
from py4j.java_gateway import java_import

gateway = launch_py4j_server()

# Import the SimpleNLG classes
java_import(gateway.jvm, "simplenlg.features.*")
java_import(gateway.jvm, "simplenlg.realiser.*")

# Define aliases so that we don't have to use the gateway.jvm prefix.
NPPhraseSpec = gateway.jvm.NPPhraseSpec
PPPhraseSpec = gateway.jvm.PPPhraseSpec
SPhraseSpec = gateway.jvm.SPhraseSpec
InterrogativeType = gateway.jvm.InterrogativeType
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

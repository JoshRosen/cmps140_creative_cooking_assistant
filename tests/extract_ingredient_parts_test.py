"""
Accuracy tests for the extract_ingredient_parts() function.
The test data is automatically loaded from a Google Docs spreadsheet.

TODO: Before we submit the project code, bundle a csv file with this code.
"""
import urllib2
import csv
from nlu.recipes import extract_ingredient_parts


TESTDATA_URL = "https://spreadsheets.google.com/pub?hl=en&hl=en&key=0AvQ9-2eaIan0dHF5QXloVU54SEppamloR2tmRFZlbXc&output=csv"


def main():
    """
    Run the accuracy tests.
    """
    skipped = 0
    passed = 0
    failed = 0
    testdata = csv.reader(urllib2.urlopen(TESTDATA_URL))
    testdata.next()  # Skip header
    for case in testdata:
        if len(case) < 4:
            skipped += 1
            continue  # Skip incomplete testcases
        expected = {
            'quantity': case[1],
            'unit': case[2],
            'modifiers': case[3],
            'base_ingredient': case[4],
        }
        for key in expected.keys():
            if not expected[key]:
                del expected[key]
        actual = extract_ingredient_parts(case[0])
        if actual != expected:
            print "Expected: %s" % str(expected)
            print "  Actual: %s" % str(actual)
            print
            failed += 1
        else:
            passed += 1
    print "Skipped: %i" % skipped
    print " Passed: %i" % passed
    print " Failed: %i" % failed
    print "  Total: %i" % (failed + skipped + passed)


if __name__ == "__main__":
    main()

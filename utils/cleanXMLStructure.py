import argparse
import json
import operator

from collections import Counter
from functools import reduce

if __name__ == '__main__':
    '''
    Simplifies the json structure extracted by ./exploreXMLStructure.py
    In particular, it gets rid of useless XML tags and indicates recursion
    of tags if need be.

    Inputs:
        * path to input json file
        * path to output json file
    '''

    # Read CLI arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', dest='inputFilePath',
        help='Path to input file')
    parser.add_argument('-o', dest='outputFilePath',
        help='Path to output file')
    args = parser.parse_args()

    # CONSTANTS
    stopKeys = [
        'div', 'p', 'br', 'font', 'i', 'ol', 'li', 'b',
        'table', 'sup', 'sub', 'em', 'ul', 'hr',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong',
        'attributes'
    ]

    def recKeys(tree):
        '''Returns the array of keys of all nested dicts of a given dict.'''

        if isinstance(tree, dict):
            return reduce(operator.add, [list(tree.keys())] + [recKeys(tree[key]) for key in tree])
        else:
            return []

    def recDictCleaning(currentKey, tree, alreadyRec):
        '''Cleans a nested json dict from useless xml tags.'''

        if isinstance(tree, list):
            return tree

        rtree = dict()
        for key in tree:
            if (not key in stopKeys) or (key == 'attributes' and len(tree[key]) > 0):
                # In case there seems to be a recursion,
                # store all recursive keys and count them by type.
                if key == currentKey and not alreadyRec:
                    rtree['*REC'] = Counter(recKeys(recDictCleaning(key, tree[key], True)))
                else:
                    rtree[key] = recDictCleaning(key, tree[key], alreadyRec)

        return rtree

    # Load JSON data
    with open(args.inputFilePath) as f:
        data = json.load(f)

    # Clean loaded dict
    cleanedData = recDictCleaning(None, data, False)

    # Output JSON data
    with open(args.outputFilePath, 'w') as f:
        f.write(json.dumps(cleanedData))

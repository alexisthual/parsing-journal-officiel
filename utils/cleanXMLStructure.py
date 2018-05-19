import argparse
import json

if __name__ == '__main__':
    # Read CLI arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', dest='inputFilePath',
        help='Path to input file')
    parser.add_argument('-o', dest='outputFilePath',
        help='Path to output file')
    args = parser.parse_args()

    # CONSTANTS
    stopKeys = ['div', 'p', 'br', 'font', 'i', 'ol', 'li', 'b', 'attributes']

    def recDictCleaning(key, tree):
        if isinstance(tree, list):
            return tree

        rtree = dict()
        for k in tree:
            if (not k in stopKeys) or (k == 'attributes' and len(tree[k]) > 0):
                if k == key:
                    rtree['*REC'] = list(set(recDictCleaning(k, tree[k])))
                else:
                    rtree[k] = recDictCleaning(k, tree[k])

        return rtree

    # Load JSON data
    with open(args.inputFilePath) as f:
        data = json.load(f)

    # Clean loaded dict
    cleanedData = recDictCleaning(None, data)

    # Output JSON data
    with open(args.outputFilePath, 'w') as f:
        f.write(json.dumps(cleanedData))

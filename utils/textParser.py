import re

class textParser:
    # def __init__(self):
    #     pass

    @staticmethod
    def parseText(text, noNewLine=False):
        parsedText = text

        if noNewLine:
            parsedText = re.sub('[\n]+', ' ', parsedText)

        parsedText = re.sub('[\t]', '', parsedText)
        parsedText = re.sub('(\s*[\n]+\s*)+', '\n', parsedText)
        parsedText = re.sub(' +', ' ', parsedText)
        parsedText = parsedText.strip()

        return parsedText

import re

class textParser:
    @staticmethod
    def parseTitle(text):
        """
        Input: string.
        Output: parsed string.
        """

        # Removes special characters and spaces
        rx = re.compile('\W+')
        parsedText = rx.sub(' ', text).strip()

        return parsedText

    @staticmethod
    def parseText(text, noNewLine=False):
        """
        Input: string.
        Output: parsed string.
        """

        parsedText = text

        if noNewLine:
            parsedText = re.sub('[\n]+', ' ', parsedText)

        parsedText = re.sub('[\t]', '', parsedText)
        parsedText = re.sub('\s*\n\s*', '\n', parsedText)
        parsedText = re.sub(' +', ' ', parsedText)
        parsedText = parsedText.strip()

        return parsedText

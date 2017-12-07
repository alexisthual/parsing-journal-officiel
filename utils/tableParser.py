from bs4 import BeautifulSoup
from .textParser import textParser


class tableParser:
    def __init__(self):
        pass

    def parseColumns(self, cols):
        columns = []
        for c in cols:
            columns.append(textParser.parseText(c.get_text(), noNewLine=True))

        return columns

    def updateRowspanAccu(self, rowspan, text, index, cols=1):
        for i in range(rowspan - 1):
            for j in range(cols):
                try:
                    self.rowspanAccu[i][index + j] = text
                except IndexError:
                    self.rowspanAccu.append({(index + j): text})

    def parseRow(self, row, tag):
        rowspanInfo = self.rowspanAccu.pop(0)
        columns = []
        rowspanCurrentInfo = {}

        j = 0
        for c in row.find_all(tag):
            text = textParser.parseText(c.get_text(), noNewLine=True)
            while j in rowspanInfo:
                columns.append(rowspanInfo[j])
                j += 1

            # Handling current rowspan and colspan
            try:
                colspan = int(c['colspan'])
            except KeyError:
                colspan = None

            try:
                rowspan = int(c['rowspan'])
            except KeyError:
                rowspan = None

            if rowspan:
                self.updateRowspanAccu(rowspan, text, j, colspan or 1)

            if colspan:
                for _ in range(colspan - 1):
                    columns.append(text)
                    j += 1


            columns.append(text)
            j += 1

        if len(self.rowspanAccu) == 0:
            self.rowspanAccu.append(rowspanCurrentInfo)
        else:
            self.rowspanAccu[0] = {**self.rowspanAccu[0], **rowspanCurrentInfo}

        return columns

    def findTh(self):
        for row in self.tableRows:
            if len(row.find_all('th')) == 0:
                break
            else:
                self.startIndex += 1
                parsedRow = self.parseRow(row, 'th')
                self.th.append(parsedRow)

    def toJson(self, htmlText):
        soup = BeautifulSoup(str(htmlText), 'html.parser')
        self.rowspanAccu = [{}]
        self.startIndex = 0
        self.th = []
        self.rows = []

        # One assumes the first rows carry the column information
        # and that they use th tags
        self.tableRows = soup.find_all('tr')
        self.findTh()

        if len(self.tableRows) > self.startIndex:
            for row in self.tableRows[self.startIndex:]:
                parsedRow = self.parseRow(row, 'td')
                self.rows.append(parsedRow)

        return {
            'thRows': self.th,
            'tdRows': self.rows
        }

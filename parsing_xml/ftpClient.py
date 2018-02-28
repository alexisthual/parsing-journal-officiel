import os
from ftplib import FTP


class FTPClient:
    def __init__(self, outputFolder):
        '''Inits connexion with the distant FTP server.'''

        self.ftp = FTP('ftp://echanges.dila.gouv.fr/')
        self.outputFolder = outputFolder

    def downloadFolder(self, dirPath):
        '''Downloads all files in a given directory.'''

        pwd = self.ftp.pwd()

        for fileName in self.ftp.dir(os.path.join(pwd, dirPath)):
            if re.match('.*2018.*\.tar\.gz', fileName):
                with open(os.path.join(self.outputFolder, fileName), 'wb') as f:
                    self.ftp.retrbinary('RETR {}'.format(fileName), f.write)
                    f.close()


# %% Test Cell
outputFolder = '/home/alexis/parsing-journal-officiel/parsing_xml/data/JORFSIMPLE'
ftpClient = FTPClient(outputFolder)
ftpClient.downloadFolder('OPENDATA/JORFSIMPLE')

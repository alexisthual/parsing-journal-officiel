import os
import re
from ftplib import FTP
from tqdm import tqdm


class FTPClient:
    def __init__(self, outputFolder, verbose=False):
        '''Inits connexion with the distant FTP server.'''

        # ping echanges.dila.gouv.fr
        # 185.24.187.136
        self.ftp = FTP('echanges.dila.gouv.fr')
        self.ftp.login()
        self.outputFolder = outputFolder
        self.verbose = verbose

    def retrieveFiles(self, dirPath):
        '''Downloads all files in a given directory.'''

        self.ftp.cwd(dirPath)
        fileNames = self.ftp.nlst()

        if self.verbose:
            print('Retrieved file list.')

        fileNames = list(filter(lambda x: re.match('.*2018.*\-.*\.tar\.gz', x), fileNames))

        if self.verbose:
            print('Downloading tarballs...')

        for fileName in tqdm(fileNames):
            if not re.match('.*Freemium.*', fileName):
                with open(os.path.join(self.outputFolder, fileName), 'wb') as f:
                    self.ftp.retrbinary('RETR {}'.format(fileName), f.write)
                    f.close()

    def terminate(self):
        self.ftp.quit()


# %% Test Cell
outputFolder = '/home/alexis/parsing-journal-officiel/parsing_xml/data/JORFSIMPLE/tarballs/'
ftpClient = FTPClient(outputFolder, verbose=True)
ftpClient.retrieveFiles('JORFSIMPLE')
ftpClient.terminate()

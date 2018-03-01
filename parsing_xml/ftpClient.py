import os
import re
from ftplib import FTP
from tqdm import tqdm


class FTPClient:
    def __init__(self, verbose=False):
        '''Inits connexion with the distant FTP server.'''

        # ping echanges.dila.gouv.fr
        # 185.24.187.136
        self.ftp = FTP('echanges.dila.gouv.fr')
        self.ftp.login()
        self.verbose = verbose

    def retrieveFiles(self, dirPath, outputFolder, regex=None):
        '''Downloads all files in a given directory.'''

        self.ftp.cwd(dirPath)
        fileNames = self.ftp.nlst()

        if self.verbose:
            print('Retrieved file list.')

        if regex:
            fileNames = list(filter(lambda x: re.match(regex, x), fileNames))

        if self.verbose:
            print('Downloading tarballs...')

        for fileName in tqdm(fileNames):
            if not re.match('.*Freemium.*', fileName):
                with open(os.path.join(outputFolder, fileName), 'wb') as f:
                    self.ftp.retrbinary('RETR {}'.format(fileName), f.write)
                    f.close()

    def terminate(self):
        self.ftp.quit()


# %% Test Cell
ftpClient = FTPClient(verbose=True)
ftpClient.retrieveFiles(
    'JORFSIMPLE',
    '/home/alexis/parsing-journal-officiel/parsing_xml/data/JORFSIMPLE/tarballs/',
    regex='.*2018.*\-.*\.tar\.gz'
)
ftpClient.terminate()

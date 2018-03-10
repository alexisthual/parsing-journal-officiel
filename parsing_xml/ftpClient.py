import os
import re
from ftplib import FTP
from tqdm import tqdm


class FTPClient:
    def __init__(self, host, verbose=False):
        '''Inits connexion with the distant FTP server.'''

        self.verbose = verbose

        if self.verbose:
            print('Attempting connexion to {}...'.format(host))

        # ping echanges.dila.gouv.fr
        # 185.24.187.136
        self.host = host
        self.ftp = FTP(self.host)
        self.ftp.login()

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
            definitiveOutputFolder = outputFolder

            # If the file's name doesn't contain 'Freemium', then it is
            # an incremental folder.
            if not re.match('.*Freemium.*', fileName):
                definitiveOutputFolder = os.path.join(outputFolder, 'incremental')

                if re.match('.*\.tar\.gz', fileName):
                    with open(os.path.join(definitiveOutputFolder, fileName), 'wb') as f:
                        self.ftp.retrbinary('RETR {}'.format(fileName), f.write)
                        f.close()

    def terminate(self):
        '''Terminate FTP connexion.'''

        self.ftp.quit()

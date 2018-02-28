import os
from ftplib import FTP
from tqdm import tqdm


class FTPClient:
    def __init__(self, outputFolder):
        '''Inits connexion with the distant FTP server.'''

        # ping echanges.dila.gouv.fr
        # 185.24.187.136
        self.ftp = FTP('echanges.dila.gouv.fr')
        self.ftp.login()
        self.outputFolder = outputFolder

    def downloadFolder(self, dirPath):
        '''Downloads all files in a given directory.'''

        pwd = self.ftp.pwd()
        print(self.ftp.dir('JORFSIMPLE'))

        for lsOutputLine in tqdm(self.ftp.dir(os.path.join(pwd, dirPath))):
            print(lsOutputLine)
            if re.match('.*2018[a-zA-Z0-9]+\.tar\.gz', lsOutputLine):
                fileName = re.search('.*([a-zA-Z0-9]+)\.tar\.gz').group(1)
                with open(os.path.join(self.outputFolder, fileName), 'wb') as f:
                    self.ftp.retrbinary('RETR {}'.format(fileName), f.write)
                    f.close()


# %% Test Cell
outputFolder = '/home/alexis/parsing-journal-officiel/parsing_xml/data/JORFSIMPLE'
ftpClient = FTPClient(outputFolder)
ftpClient.downloadFolder('JORFSIMPLE')

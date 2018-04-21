import os
import re
import tarfile
from tqdm import tqdm


class FileExtracter:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def extractAll(self, fromDir, toDir):
        '''Extracts all files from all tarballs present in a given directory.'''

        if self.verbose:
            print('Extracting tarballs...')

        for fileName in tqdm(os.listdir(fromDir)):
            if re.match('.*\.tar\.gz', fileName):
                tar = tarfile.open(os.path.join(fromDir, fileName))
                tar.extractall(path=toDir)
                tar.close()

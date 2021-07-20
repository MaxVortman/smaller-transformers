import tarfile
from io import BytesIO

import requests
import os


class Leipzig:
    DOWNLOAD_URL = 'http://pcai056.informatik.uni-leipzig.de/downloads/corpora'
    _gist_meta_url = 'https://gist.githubusercontent.com/derlin/917a64e6412de6c503f3f52e0878f919/raw/leipzig_meta.json'

    def __init__(self, version=None):
        url = self._gist_meta_url
        if version is not None:
            url = url.replace('raw', f'raw/{version}')
        try:
            leipzig_meta = requests.get(url).json()
        except:
            raise Exception(f'Could not fetch meta from {url}.')
        self.code2lang = leipzig_meta['languages']
        self.lang2code = {v: k for k, v in self.code2lang.items()}

    @staticmethod
    def download_words(url):
        """Download sentences from a leipzig resource URL."""
        # get tar archive
        res = requests.get(url)
        # extract sentences file from archive
        tar = tarfile.open(mode='r:gz', fileobj=BytesIO(res.content))
        tar_info = [member for member in tar.getmembers() if member.name.endswith('words.txt')][0]
        handle = tar.extractfile(tar_info)
        # read sentence file
        raw_text = handle.read().decode('utf-8')
        return [line.split('\t')[1] for line in raw_text.split('\n') if '\t' in line]


    def retry_download(self, download, code, typ, year, size):
        print(f'Processing {code} {self.code2lang[code]}...', end=' ', flush=True)
        resource = f"{code}_{typ}_{year}_{size}.tar.gz"
        print(resource, end=' ', flush=True)
        print()
        try:
            return download(f'{self.DOWNLOAD_URL}/{resource}')
        except tarfile.ReadError:
            return self.retry_download(download, code, typ, int(year) - 1, size)



    def download_all(self, download_folder, language_codes=None, filename='{code}.{size}.txt',
                     size='10K', typ='wikipedia', year='2016',
                     normalize_func=lambda t: t, filter_func=lambda t: True):
        """
        Download all resources into a folder. For size, typ and year argument, see LeipzigResourceFinder
        :param download_folder: the download folder
        :param language_codes: a list of language codes to download, will download everything if not set
        :param filename: available placeholders are code, size and typ
        :param size: the size to prioritize
        :param typ: the type of resource to prioritize, e.g. 'wikipedia', 'web', etc.
        :param year: the year to prioritize
        :param normalize_func: an optional function called on each sentence
        :param filter_func: an optional filter to exclude sentences
        """
        os.makedirs(download_folder, exist_ok=True)

        if language_codes is None:
            language_codes = list(self.code2lang.keys())

        for code in language_codes:
            variant = None
            outpath = os.path.join(download_folder, filename.format(code=code, typ=typ, size=size))
            if not os.path.exists(outpath):
                try:
                    lines = [
                        normalize_func(l)
                        for l in self.retry_download(self.download_words, code, typ, year, size)
                        if len(l) > 0 and not l.isspace() and filter_func(l)
                    ]
                    if len(lines):
                        with open(outpath, 'w') as f:
                            f.write('\n'.join(lines))
                        print(f'{len(lines)} lines. OK')
                    else:
                        print('no line.')
                except Exception as e:
                    print('ERROR', e)
                    raise e



if __name__ == "__main__":
    corpora = Leipzig()
    corpora.download_all("data", ["ukr", "eng", "rus"], size='100K', year='2021')

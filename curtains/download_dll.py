import os
import zipfile
from distutils.core import setup


def download_latest_release(user, repo, asset_name):
    command = f'curl -fsSL github.com/{user}/{repo}/releases/download/latest/{asset_name} -O'
    os.system(command)

def create_assets_dir():
    if not os.path.exists(assets_dir):
        os.mkdir('assets')

def unpack_dll_files():
    zip_file = zipfile.ZipFile((basedir + '/' + asset_name), 'r')
    for file in zip_file.namelist():
        if file in dll_files:
            zip_file.extract(file,assets_dir)

    zip_file.close()

if __name__ == '__main__':
    user = 'AbortLarboard'
    repo = 'curtains_dev'
    asset_name = 'dll_assets.zip'
    dll_files = ['Hide.dll', 'Hide_32bit.dll', 'Unhide.dll', 'Unhide_32bit.dll']
    basedir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = basedir + '/assets'

    download_latest_release(user, repo, asset_name)
    create_assets_dir()
    unpack_dll_files()
    os.remove(basedir + '/' + asset_name)

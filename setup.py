import glob
import os
import platform
import shutil
import sys

from distutils.command.install import install
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.dist import Distribution
from urllib.request import urlretrieve


# TODO: Need to get version from somewhere smart
# consider replacing in setup script before packaging and uploading to twine
global version 
version = "1.3.450"

def get_platform_suffix():
    if sys.platform == "darwin":
        return "macos.tar.gz"
    elif sys.platform == "win32":
        return "win.zip"
    elif sys.platform == "linux":
        m = platform.machine()
        if m == "x86_64":
            return "linux-amd64.tar.gz"
        elif m == "aarch64":
            return "linux-arm64.tar.gz"
        # TODO: detect RHEL7 since we have a special download for it
    else:
        raise Exception("Platform not supported")

def download_quarto(version, suffix):
    quarto_url = f"https://github.com/quarto-dev/quarto-cli/releases/download/v{version}/quarto-{version}-{suffix}"
    print("Downloading", quarto_url)

    try:
        name, resp = urlretrieve(quarto_url)
        return name
    except Exception as e:
        print("Error downloading Quarto:", e)
    

class CustomInstall(install):
    def run(self):
        
        suffix = get_platform_suffix()
        name = download_quarto(version, suffix)

        output_location = f"quarto_cli/quarto-{version}"
        os.makedirs(output_location, exist_ok=True)

        if suffix.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(name, 'r') as zip_ref:
                zip_ref.extractall(output_location)
        elif suffix.startswith("linux"):
            import tarfile
            with tarfile.open(name) as tf:
                tf.extractall(Path(output_location).parent.resolve())
        else:
            import tarfile
            with tarfile.open(name) as tf:
                tf.extractall(output_location)
        
        # Move the bin/share directory up a level
        binFrom = os.path.join(output_location, "bin")
        binTo = os.path.join("quarto_cli", "bin")
        print(f"Moving {binFrom} to {binTo}")
        shutil.move(binFrom, binTo)
        shutil.move(os.path.join(output_location, "share"), os.path.join("quarto_cli", "share"))
            
        # Remove the old directory
        shutil.rmtree(output_location)


        super().run()

setup(
    name='quarto_cli',
    version=version,
    description='Open-source scientific and technical publishing system built on Pandoc.',
    packages=find_packages(),
    cmdclass={
        'install': CustomInstall,
    },
    install_requires=[
        'jupyter',
        'nbclient',
        'wheel',
    ],
)
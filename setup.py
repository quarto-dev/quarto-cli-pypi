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

# The version number for this installation
print("Current working directory:", os.getcwd())

here = os.path.abspath(os.path.dirname(__file__))
print(f"HERE: {here}")
print(os.listdir(here))
version_file = os.path.join(here, 'version.txt')
version = open(version_file).read().strip()
target_directory = "quarto_cli"

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

def move_pkg_subdir(name, fromDir, toDir):
    mvFrom = os.path.join(fromDir, name)
    mvto = os.path.join(toDir, name)
    print(f"Moving {mvFrom} to {mvto}")
    shutil.move(mvFrom, mvto)    

class CustomInstall(install):
    def run(self):
        
        print("Downloading and installing quarto-cli binaries...")
        suffix = get_platform_suffix()
        name = download_quarto(version, suffix)

        output_location = f"{target_directory}/quarto-{version}"
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
        move_pkg_subdir("bin", output_location, target_directory)
        move_pkg_subdir("share", output_location, target_directory)
            
        # Remove the old directory
        shutil.rmtree(output_location)

        super().run()

setup(
    name='quarto-cli',
    version=version,
    description='Open-source scientific and technical publishing system built on Pandoc.',
    packages=find_packages(),
    package_data={
        '': ['version.txt']
    },
    include_package_data=True,
    cmdclass={
        'install': CustomInstall,
    },
    install_requires=[
        'jupyter',
        'nbclient',
        'wheel',
    ],
)
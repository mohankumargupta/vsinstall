import requests
from pathlib import Path
from zipfile import ZipFile
import sys
from tempfile import TemporaryFile, TemporaryDirectory
import click
import subprocess

VSCODE_URL = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-archive"
#OUTPUT_FOLDER = "vscode-php`"
zip_size = 0

def download_file(url: str, output_file: Path, download_size):
    print("Downloading vscode...")
    downloaded = 0
    # NOTE the stream=True parameter below
    with click.progressbar(length=download_size, label="Downloading") as progress_bar:
        with requests.get(url, stream=True) as r:
            if r.status_code != 200:
                pass
            r.raise_for_status()
            #with open(output_file, 'wb') as f:
            with output_file.open('wb') as f:
                for chunk in r.iter_content(chunk_size=4096): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress_bar.update(len(chunk))
                    percentage = int((downloaded / download_size) * 100)
                    progress_bar.label = f"Downloading: {percentage}%"                    
    print("Done Downloading.")

def mkdir(dirname):
    Path(dirname).mkdir(parents=True, exist_ok=False)

def unzip(filename: Path, dirname: Path):
    print("Unzipping...")
    with ZipFile(filename) as f:
        f.extractall(dirname)
    print("Unzipping done.")

def makeDataDirectories(dirname):
    datadir = Path(dirname).joinpath("data")
    tmpdir = datadir.joinpath("tmp")
    mkdir(datadir)
    mkdir(tmpdir)

def downloadsDirectory():
    homedirectory = Path.home()
    downloads = homedirectory.joinpath("Downloads")
    return downloads

def install_vscode_portable(download_folder, size):
    fullpath = downloadsDirectory() / download_folder
    mkdir(fullpath)
    vscode_zip = fullpath / "vscode.zip"
    vscode_zip.touch()
    download_file(VSCODE_URL, vscode_zip, size)
    unzip(vscode_zip, fullpath)
    makeDataDirectories(fullpath)
    vscode_zip.unlink()
    return fullpath

def get_file_size(url: str) -> int:
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            content_length = response.headers.get('Content-Length')
            if content_length:
                return int(content_length)
            else:
                print("Content-Length header not found.")
        else:
            print(f"Failed to fetch URL. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error occurred: {e}")
    return 0  # Return 0 if size couldn't be determined






@click.command
@click.option('--name', prompt='VSCode folder name')
def vscode_install(name):
    global zip_size
    return install_vscode_portable(name, zip_size)

def main():
    global zip_size
    zip_size = get_file_size(VSCODE_URL)
    print(f"File size: {zip_size} bytes")
    vscode_folder = vscode_install()
    print(vscode_folder)
    vscode_binary = vscode_folder / "Code.exe"
    print("Success. Now opening VSCode Portable...")
    subprocess.Popen([vscode_binary])
    sys.exit(0)    

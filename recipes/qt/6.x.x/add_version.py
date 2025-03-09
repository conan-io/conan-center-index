#!/usr/bin/env python3
import sys
from hashlib import sha256
from pathlib import Path

import requests
from conan.tools.scm import Version
from tqdm.auto import tqdm

script_dir = Path(__file__).parent

# qt.io does not provide Content-Length info, so using a mirror instead.
base_url = "https://qt-mirror.dannhauer.de/archive/"

# Modules that are not available as a downloadable archive and which must be fetched from GitHub instead.
git_components = [
    "qt5",  # the superbuild root repository
    "qtcoap",
    "qtmqtt",
    "qtopcua",
]

def get_components_list(version):
    version = Version(version)
    url = f"{base_url}qt/{version.major}.{version.minor}/{version}/submodules/md5sums.txt"
    r = requests.get(url)
    r.raise_for_status()
    components = []
    for l in r.text.splitlines():
        if not l.endswith(".tar.xz"):
            continue
        components.append(l.split()[1].split("-")[0])
    return sorted(components + git_components)


def get_url(version, component):
    version = Version(version)
    if component in git_components:
        return f"https://github.com/qt/{component}/archive/refs/tags/v{version}.tar.gz"
    return f"{base_url}qt/{version.major}.{version.minor}/{version}/submodules/{component}-everywhere-src-{version}.tar.xz"


def get_download_size(session, url):
    with session.head(url) as r:
        r.raise_for_status()
        return int(r.headers["Content-Length"])


def add_source_hashes(version):
    print("Computing source archive hashes...")
    components = get_components_list(version)
    yml_path = script_dir / "sources" / f"{version}.yml"
    with requests.Session() as session:
        # Fetch sizes before downloading to check that all URLs are valid.
        urls = {component: get_url(version, component) for component in components}
        archive_sizes = {
            component: get_download_size(session, url) for component, url in tqdm(urls.items(), desc="Fetching sizes")
        }
        with yml_path.open("w") as f:
            f.write("hashes:\n")
            overall_progress = tqdm(total=sum(archive_sizes.values()), desc="Overall progress", unit="B", unit_scale=True, position=0)
            for component in components:
                url = urls[component]
                file_size = archive_sizes[component]
                progress = tqdm(total=file_size, unit="B", unit_scale=True, desc=component, leave=False, position=1)
                sha256sum = sha256()
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=100_000):
                        overall_progress.update(len(chunk))
                        progress.update(len(chunk))
                        sha256sum.update(chunk)
                progress.close()
                hash = sha256sum.hexdigest().lower()
                f.write(f'  {component + ":": <19} "{hash}"  # {file_size / 1_000_000: 6.1f} MB\n')
                f.flush()
            overall_progress.close()
            f.write("git_only:\n")
            for component in git_components:
                f.write(f'  - {component}\n')

def fetch_gitmodules(version):
    conf_path = script_dir.joinpath("qtmodules", f"{version}.conf")
    print(f"Adding qtmodules/{version}.conf...")
    url = f"https://raw.githubusercontent.com/qt/qt5/refs/tags/v{version}/.gitmodules"
    r = requests.get(url)
    r.raise_for_status()
    conf_path.write_text(r.text)

if __name__ == "__main__":
    version = sys.argv[1]
    fetch_gitmodules(version)
    add_source_hashes(version)

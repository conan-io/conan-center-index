#!/bin/env python
# Usage: ./update_hashes.py [rust_version]
# Updates all sha256 hashes in conandata.yml using the .sha256 files available on the Rust server.

import re
import sys
from pathlib import Path

import requests


def get_hash(url):
    sha_url = f"{url}.sha256"
    response = requests.get(sha_url)
    response.raise_for_status()
    return response.text.split()[0].strip()


def process(match, version):
    url = match[3].strip().strip("'").strip('"')
    hash = match[4].strip().strip("'").strip('"')
    if version is None or version in url:
        print(f"  Processing {url}", flush=True)
        hash = get_hash(url)
    return f'{match[1]}{match[2]}url: "{url}"\n{match[1]}  sha256: "{hash}"'


def update_hashes(yaml_path, version):
    yaml_path = Path(yaml_path)
    content = yaml_path.read_text()
    content = re.sub(r'^( +)([- ] )url: (.+)\n\1  sha256: (.+)$', lambda m: process(m, version), content, flags=re.M)
    yaml_path.write_text(content)


if __name__ == "__main__":
    rust_version = sys.argv[1] if len(sys.argv) > 1 else None
    yaml_path = Path(__file__).parent.joinpath("conandata.yml")
    update_hashes(yaml_path, rust_version)

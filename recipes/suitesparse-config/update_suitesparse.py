#!/usr/bin/env python3

# Usage: ./update_suitesparse.py <new_version>
#
# Updates all `suitesparse-*` sub-packages based on the source archive automatically downloaded of the given version.

import hashlib
import io
import re
import sys
import tarfile
import textwrap
from pathlib import Path

import requests
import yaml
from conan.tools.scm import Version

recipes_root = Path(__file__).resolve().parent.parent

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(str, quoted_presenter)

def download(url):
    print(f"Downloading {url}...")
    r = requests.get(url)
    r.raise_for_status()
    return r.content


def sha256(data):
    sha = hashlib.sha256()
    sha.update(data)
    return sha.hexdigest()


def extract_version(content):
    major = re.search(r"^set *\( *(\w+)_VERSION_MAJOR +(\d+) ", content, re.M).group(2)
    minor = re.search(r"^set *\( *(\w+)_VERSION_MINOR +(\d+) ", content, re.M).group(2)
    sub = re.search(r"^set *\( *(\w+)_VERSION_(?:SUB|PATCH|UPDATE) +(\d+) ", content, re.M).group(2)
    return f"{major}.{minor}.{sub}"


def load_versions(tar_gz_bytes):
    versions = {}
    tar_gz_file = io.BytesIO(tar_gz_bytes)
    with tarfile.open(fileobj=tar_gz_file, mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            if m := re.fullmatch(r"SuiteSparse-[^/]+/(\w+)/CMakeLists.txt", member.name):
                name = m.group(1)
                if name in ["Example", "GraphBLAS", "CSparse"]:
                    continue
                content = tar.extractfile(member).read().decode("utf8")
                pkg_name = "suitesparse-config" if name == "SuiteSparse_config" else "suitesparse-" + name.lower()
                versions[pkg_name] = extract_version(content)
            elif member.name.endswith("GraphBLAS_version.cmake"):
                content = tar.extractfile(member).read().decode("utf8")
                versions["suitesparse-graphblas"] = extract_version(content)
    return versions


def update_config_yml(pkg_name, new_version):
    config_yml_path = recipes_root / pkg_name / "config.yml"
    info = yaml.safe_load(config_yml_path.read_text("utf8"))
    latest = str(max(Version(v) for v in info["versions"]))
    if latest == new_version:
        print(f"{pkg_name}: already up-to-date ({latest})")
        return False
    print(f"{pkg_name}: updating from {latest} to {new_version}...")
    content = config_yml_path.read_text("utf8")
    content, n = re.subn("versions:\n", f'versions:\n  "{new_version}":\n    folder: all\n', content)
    if n != 1:
        raise ValueError("Failed to update versions in config.yml")
    config_yml_path.write_text(content, "utf8")
    return True

def update_conandata_yml(pkg_name, new_version, url, archive_hash):
    config_yml_path = recipes_root / pkg_name / "all" / "conandata.yml"
    content = config_yml_path.read_text("utf8")
    conandata = yaml.safe_load(content)
    content, n = re.subn("sources:\n", f'sources:\n  "{new_version}":\n    url: "{url}"\n    sha256: "{archive_hash}"\n', content)
    if n != 1:
        raise ValueError("Failed to update sources in conandata.yml")
    if "patches" in conandata:
        newest = str(max(Version(v) for v in conandata["patches"]))
        patches = conandata["patches"][newest]
        patches_yaml = textwrap.indent(yaml.dump(patches, default_flow_style=False, sort_keys=False), "    ")
        patches_yaml = re.sub(r'"(\w+)":', r'\1:', patches_yaml)
        content, n = re.subn("patches:\n", f'patches:\n  "{new_version}":\n{patches_yaml}', content)
        if n != 1:
            raise ValueError("Failed to update patches in conandata.yml")
    config_yml_path.write_text(content, "utf8")


def update_conanfile_py(pkg_name, versions):
    conanfile_py_path = recipes_root / pkg_name / "all" / "conanfile.py"
    content = conanfile_py_path.read_text("utf8")
    # update dependency versions
    for pkg, new_version in versions.items():
        content = re.sub(rf'"{pkg}/\S+"', f'"{pkg}/{new_version}"', content)
    conanfile_py_path.write_text(content, "utf8")


def main(suitesparse_version):
    suitesparse_url = (
        f"https://github.com/DrTimothyAldenDavis/SuiteSparse/archive/refs/tags/v{suitesparse_version}.tar.gz"
    )
    tar_gz_bytes = download(suitesparse_url)
    suitesparse_hash = sha256(tar_gz_bytes)
    print("Reading versions from CMakeLists.txt files...")
    versions = load_versions(tar_gz_bytes)
    for pkg_name, new_version in versions.items():
        needs_updating = update_config_yml(pkg_name, new_version)
        if needs_updating:
            if pkg_name == "suitesparse-graphblas":
                graphblas_url = f"https://github.com/DrTimothyAldenDavis/GraphBLAS/archive/refs/tags/v{new_version}.tar.gz"
                graphblas_hash = sha256(download(graphblas_url))
                update_conandata_yml(pkg_name, new_version, graphblas_url, graphblas_hash)
            else:
                update_conandata_yml(pkg_name, new_version, suitesparse_url, suitesparse_hash)
        update_conanfile_py(pkg_name, versions)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./update_suitesparse.py <new_version>")
        sys.exit(1)
    suitesparse_version = sys.argv[1]
    main(suitesparse_version)

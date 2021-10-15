#!/usr/bin/env python

import hashlib
import json
import subprocess
from os import environ
from pathlib import Path

from conans.client.profile_loader import read_profile

_dssl_req_patterns = ['trassir/', 'bintray/']


def dssl_req_filter(line):
    return not any((pattern in str(line) for pattern in _dssl_req_patterns))


def conan_run(args):
    cmd = ['conan']
    if 'CONAN_DOCKER_IMAGE' in environ and environ['CONAN_DOCKER_IMAGE']:
        docker_path = Path('.conan-docker')
        if not docker_path.exists():
            docker_path.mkdir()
            docker_path.chmod(0o777)
            Path('sources').chmod(0o777)
        mount_ws = ':'.join([
            environ['GITHUB_WORKSPACE'] + '/sources',
            '/home/conan/sources'])
        mount_conan = ':'.join([
            environ['GITHUB_WORKSPACE'] + '/.conan-docker',
            '/home/conan/.conan'])
        cmd = ['docker', 'run',
               '-v', mount_ws,
               '-v', mount_conan,
               environ['CONAN_DOCKER_IMAGE'],
               ] + cmd
    cmd += args
    subprocess.check_call(cmd)


def _is_gha_buildable(line):
    if line.startswith('#'):
        return False
    if '# GHA: ignore' in line:
        return False
    if '@' in line:
        return False
    if '/' not in line:
        return False
    return True


def list_installed_packages():
    installed_packages = []
    conan_run(['search', '--json',
               str(Path('sources', 'installed.json')), '*'])
    instaled_path = Path('sources', 'installed.json')
    with open(str(instaled_path), 'r', encoding='utf8') as file:
        installed = json.load(file)
    if installed['results']:
        for pkg in installed['results'][0]['items']:
            if _is_gha_buildable(pkg['recipe']['id']):
                installed_packages.append(pkg['recipe']['id'])
    return installed_packages


class PackageReference():
    def _possible_conanfile_locations(self):
        file = 'conanfile.py'
        yield Path('recipes', self.name, self.version, file)
        full_ver = self.version.split('.')
        for i in range(len(full_ver) - 1, 0, -1):
            for j in range(len(full_ver) - i, -1, -1):
                masked_ver = full_ver[:i] + j * ['x']
                yield Path('recipes',
                           self.name,
                           '.'.join(masked_ver),
                           file)
        yield Path('recipes', self.name, 'all', file)

    def __init__(self, strref):
        if '# GHA: noexport' in strref:
            strref_stripped = strref[:strref.index('# GHA: noexport')].strip()
            self.export_recipe = False
        else:
            strref_stripped = strref.strip()
            self.export_recipe = True
        if '/' not in strref_stripped:
            raise RuntimeError(f'package reference `{strref}` \
                does not contain `/`')
        self.name, self.version = strref_stripped.split('/')
        self.conanfile_path = None
        self.conanfile = ""
        self.md5sum = None
        if not self.export_recipe:
            return
        for loc in self._possible_conanfile_locations():
            print(f'searching for conanfile.py in {loc}')
            if loc.is_file():
                self.conanfile_path = loc
                break
        if not self.conanfile_path:
            raise RuntimeError(f'Recipe for package \
                {self.ref()} could not be found')
        with open(self.conanfile_path, 'rb') as file:
            self.conanfile = file.read()
        md5 = hashlib.md5()
        md5.update(self.conanfile)
        self.md5sum = md5.hexdigest()

    def export(self):
        if self.export_recipe:
            conan_run(['export',
                       str(Path('sources', self.conanfile_path)),
                       self.ref() + '@_/_'])
        else:
            print(f"exporting recipe for {self.ref()} \
                is disabled in {environ['CONAN_TXT']}")

    def ref(self):
        return '/'.join([self.name, self.version])

    def __str__(self):
        return f'name={self.name:<16}\t' + \
               f'ver={self.version:<16}\t' + \
               f'md5={self.md5sum}\t' + \
               f'src={self.conanfile_path}'


class ConanfileReqInfo:
    def __init__(self,
                 conanfile: Path,
                 conanprofile: Path,
                 conanfile_required: bool):
        self.all_packages = {}
        if conanfile.exists() and conanprofile.exists():
            conanprofile, _ = read_profile(str(conanprofile), '.', '.')
            for _, packages in conanprofile.build_requires.items():
                for package in packages:
                    self.add_package(str(package))

            with open(str(conanfile), encoding='utf8') as txt_file:
                for strline in txt_file.read().splitlines():
                    self.add_package(strline)
        elif conanfile_required:
            raise RuntimeError(f'File {conanfile} or \
                {conanprofile} does not exist')

    def add_package(self, strline):
        if not _is_gha_buildable(strline):
            return
        package = PackageReference(strline)
        self.packages[package.name] = package

    def export(self):
        for package in self.packages:
            package.export()

    @property
    def packages(self):
        return self.all_packages

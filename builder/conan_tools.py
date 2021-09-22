#!/usr/bin/env python

from os import path, environ, mkdir, chmod
import subprocess
import hashlib
import json


def conan_run(args):
    cmd = ['conan']
    if 'CONAN_DOCKER_IMAGE' in environ and environ['CONAN_DOCKER_IMAGE']:
        if not path.exists('.conan-docker'):
            mkdir('.conan-docker')
            chmod('.conan-docker', 0o777)
            chmod('sources', 0o777)
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
               path.join('sources', 'installed.json'), '*'])
    instaled_path = path.join('sources', 'installed.json')
    with open(instaled_path, 'r', encoding='utf8') as file:
        installed = json.load(file)
    if installed['results']:
        for pkg in installed['results'][0]['items']:
            if _is_gha_buildable(pkg['recipe']['id']):
                installed_packages.append(pkg['recipe']['id'])
    return installed_packages


class PackageReference():
    def _possible_conanfile_locations(self):
        file = 'conanfile.py'
        yield path.join('recipes', self.name, self.version, file)
        full_ver = self.version.split('.')
        for i in range(len(full_ver) - 1, 0, -1):
            for j in range(len(full_ver) - i, -1, -1):
                masked_ver = full_ver[:i] + j * ['x']
                yield path.join('recipes',
                                self.name,
                                '.'.join(masked_ver),
                                file)
        yield path.join('recipes', self.name, 'all', file)

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
            if path.isfile(loc):
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
                       path.join('sources', self.conanfile_path),
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


class ConanfileTxt():
    def __init__(self, filename, conanfile_required):
        self.packages = {}
        if path.isfile(filename):
            with open(filename, encoding='utf8') as txt_file:
                for strline in txt_file.read().splitlines():
                    self.add_package(strline)
        elif conanfile_required:
            raise RuntimeError(f'File {filename} does not exist')

    def add_package(self, strline):
        if not _is_gha_buildable(strline):
            return
        package = PackageReference(strline)
        self.packages[package.name] = package

    def export(self):
        for package in self.packages:
            package.export()

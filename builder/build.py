#!/usr/bin/env python

from os import environ, mkdir, path
import subprocess
from conans import tools
from environment import prepare_environment
from conan_tools import ConanfileTxt, list_installed_packages, conan_run


def remove_artifctory_deps_from_txt(filename):
    def wanted_line(line):
        if '@trassir/' in line.decode('utf-8'):
            return False
        return True
    conanfile_contents = []
    with open(filename, 'rb') as txt:
        conanfile_contents = txt.read().splitlines()
    conanfile_contents = list(filter(wanted_line, conanfile_contents))
    with open(filename, 'wb') as txt:
        for line in conanfile_contents:
            txt.write(line)
            txt.write('\n'.encode('utf-8'))


def print_section(message):
    print('=' * 80)
    print('   ' + message)
    print('=' * 80)


def collect_dependencies(branch_name):
    print_section(f'Collect packages info from branch {branch_name}')
    mkdir(branch_name)
    with tools.chdir(branch_name):
        repo = '/'.join([environ['GITHUB_SERVER_URL'],
                         environ['GITHUB_REPOSITORY']])
        subprocess.check_call(['git', 'clone', repo, '.'])
        subprocess.check_call(['git', 'checkout', branch_name])
        subprocess.check_call(['git', 'branch'])
        conanfile_txt = ConanfileTxt(environ['CONAN_TXT'],
                                     branch_name != 'master')
    print(f'Collected {len(conanfile_txt.packages)} packages:')
    for _, found_pkg in conanfile_txt.packages.items():
        print(found_pkg)
    return conanfile_txt


def detect_updated_packages(master_txt, branch_txt):
    '''
        Raise exception if following requirement is not satisfied:
        'updating conanfile.py must always be done with package version bump'
    '''
    inconsistent_update = False
    for name, pkg in branch_txt.packages.items():
        if name not in master_txt.packages.keys():
            print(f'CONAN_TXT: package added {pkg}')
            continue
        if master_txt.packages[name].md5sum != pkg.md5sum:
            print(('CONAN_TXT: recipe update detected\n'
                  + f'package(master): {master_txt.packages[name]}\n'
                  + f'package(branch): {pkg}'))
            if master_txt.packages[name].version == pkg.version:
                inconsistent_update = True
                print('CONAN_TXT: recipe updated but version did not')
        else:
            if master_txt.packages[name].version == pkg.version:
                print(f'CONAN_TXT: package did not change: \
                    {pkg.name}/{pkg.version}')
            else:
                pkg_master_ref = '/'.join([
                    master_txt.packages[name].name,
                    master_txt.packages[name].version])
                print('CONAN_TXT: package updated with no recipe changes: '
                      + f'{pkg_master_ref} => {pkg.name}-{pkg.version}')
        if inconsistent_update:
            raise RuntimeError('package recipe updated but version did not')


def detect_dependency_lock(installed_packages, conanfile_txt):
    '''
        Raise exception if .txt file does not contain entire dependency tree
    '''
    txt_needs_updating = False
    for installed_package in installed_packages:
        name, version = installed_package.split('/')
        if name not in conanfile_txt.packages:
            print(f"Package {name}/{version} is not mentioned \
                in {environ['CONAN_TXT']}")
            txt_needs_updating = True
            continue
        if version != conanfile_txt.packages[name].version:
            print(('Package {name}/{ver} is mentioned in {txt}'
                  + ' with different version {name}/{ver_txt}').format(
                  name=name, ver=version, txt=environ['CONAN_TXT'],
                  ver_txt=conanfile_txt.packages[name].version))
            txt_needs_updating = True
            continue
        print(f"Package {name} is confirmed \
            by {environ['CONAN_TXT']} as {name}/{version}")
    if txt_needs_updating:
        raise RuntimeError(f"{environ['CONAN_TXT']} needs updating, \
            see packages listed above")


if __name__ == '__main__':
    UPLOAD_REMOTE = prepare_environment()

    conanfile_txt_master = collect_dependencies('master')
    if 'GITHUB_HEAD_REF' in environ and environ['GITHUB_HEAD_REF'] != '':
        conanfile_txt_head = collect_dependencies(environ['GITHUB_HEAD_REF'])
    else:
        conanfile_txt_head = conanfile_txt_master

    print_section('Ensure recipe changes accompanied with version bump')
    detect_updated_packages(conanfile_txt_master, conanfile_txt_head)

    print_section(f"Exporting all package recipes \
        referenced in {environ['CONAN_TXT']}")
    for _, package in conanfile_txt_head.packages.items():
        package.export()

    print_section(f"Building packages from {environ['CONAN_TXT']} \
        for {environ['CONAN_PROFILE']}")

    # TODO: remove this once bintray and artifactory are merged
    remove_artifctory_deps_from_txt(path.join('sources', environ['CONAN_TXT']))

    conan_run(['install',
               path.join('sources', environ['CONAN_TXT']),
               '-if', 'install_dir',
               '-pr', path.join('sources', environ['CONAN_PROFILE']),
               '--build', 'missing'])

    print_section('Enumerating installed packages')
    installed = list_installed_packages()

    print_section(f"Ensure all packages have mention \
        in {environ['CONAN_TXT']}")
    detect_dependency_lock(installed, conanfile_txt_head)

    print_section('Uploading packages')
    if installed:
        conan_run(['upload',
                   '--confirm', '--all',
                   '-r', UPLOAD_REMOTE, '*'])

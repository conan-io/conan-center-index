#!/usr/bin/env python

from os import environ
from conan_tools import conan_run


def conan_add_remote(name=None, url=None, username=None, password=None):
    conan_run(['remote', 'add', name, url, 'True'])
    if username and password:
        conan_run(['user', '--password', password, '--remote', name, username])


def prepare_environment():
    # fork main repo and set these variables to have own repo for development
    custom_remotes = \
        'REMOTES_STAGING' in environ and environ['REMOTES_STAGING'] and \
        'REMOTES_MASTER' in environ and environ['REMOTES_MASTER'] and \
        'REMOTES_USERNAME' in environ and environ['REMOTES_USERNAME'] and \
        'REMOTES_PASSWORD' in environ and environ['REMOTES_PASSWORD']

    # these interfere with conan commands
    if 'CONAN_USERNAME' in environ:
        del environ['CONAN_USERNAME']
    if 'CONAN_CHANNEL' in environ:
        del environ['CONAN_CHANNEL']

    conan_run(['config', 'install',
              'https://github.com/trassir/conan-config.git'])

    conan_run(['remote', 'clean'])

    def artifactory_repo(repo):
        return 'https://artifactory.trassir.com/artifactory/api/conan/' + repo

    official_prefix = ''
    if custom_remotes:
        official_prefix = 'official-'

    conan_add_remote(name=official_prefix + 'github-staging',
                     url=artifactory_repo('github-staging'),
                     username=environ['LDAP_USERNAME'],
                     password=environ['LDAP_PASSWORD'])
    conan_add_remote(name=official_prefix + 'github-stable',
                     url=artifactory_repo('github-stable'),
                     username=environ['LDAP_USERNAME'],
                     password=environ['LDAP_PASSWORD'])
    conan_add_remote(name='conan-center', url='https://conan.bintray.com')

    if custom_remotes:
        conan_add_remote(name='github-staging',
                         url=environ['REMOTES_STAGING'],
                         username=environ['REMOTES_USERNAME'],
                         password=environ['REMOTES_PASSWORD'])
        conan_add_remote(name='github-stable',
                         url=environ['REMOTES_MASTER'],
                         username=environ['REMOTES_USERNAME'],
                         password=environ['REMOTES_PASSWORD'])

    print('Remotes ready:')
    conan_run(['remote', 'list'])
    conan_run(['user'])

    if 'GITHUB_HEAD_REF' in environ and environ['GITHUB_HEAD_REF'] != '':
        print('Detected staging branch `{branch}`'
              .format(branch=environ['GITHUB_HEAD_REF']))
        upload_remote = 'github-staging'
    else:
        upload_remote = 'github-stable'
    print('Will upload to {remote}'.format(remote=upload_remote))

    return upload_remote

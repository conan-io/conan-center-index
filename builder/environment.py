#!/usr/bin/env python

from os import environ
from conan_tools import conan_run


def prepare_environment():
    # fork main repo and set these variables to have own repo for development
    custom_remotes = \
        'REMOTES_STAGING' in environ and environ['REMOTES_STAGING'] and \
        'REMOTES_MASTER' in environ and environ['REMOTES_MASTER'] and \
        'REMOTES_UPLOAD_USER' in environ and environ['REMOTES_UPLOAD_USER']

    # these interfere with conan commands
    if 'CONAN_USERNAME' in environ:
        del environ['CONAN_USERNAME']
    if 'CONAN_CHANNEL' in environ:
        del environ['CONAN_CHANNEL']

    conan_run(['config', 'install',
              'https://github.com/trassir/conan-config.git'])

    conan_run(['remote', 'clean'])

    trassir_org = 'https://api.bintray.com/conan/trassir/'
    if custom_remotes:
        # allow download from official repos
        conan_run(['remote', 'add', 'org-trassir-staging',
                   trassir_org + 'conan-staging', 'True'])
        conan_run(['remote', 'add', 'org-trassir-public',
                   trassir_org + 'conan-public', 'True'])
        conan_run(['remote', 'add', 'conan-center',
                   'https://conan.bintray.com', 'True'])
        # use unofficial repos for dev repo
        conan_run(['remote', 'add', 'trassir-staging',
                   environ['REMOTES_STAGING'], 'True'])
        conan_run(['remote', 'add', 'trassir-public',
                   environ['REMOTES_MASTER'], 'True'])
    else:
        conan_run(['remote', 'add', 'trassir-staging',
                   trassir_org + 'conan-staging', 'True'])
        conan_run(['remote', 'add', 'trassir-public',
                   trassir_org + 'conan-public', 'True'])
        conan_run(['remote', 'add', 'conan-center',
                   'https://conan.bintray.com', 'True'])

    print('Remotes ready:')
    conan_run(['remote', 'list'])

    if 'GITHUB_HEAD_REF' in environ and environ['GITHUB_HEAD_REF'] != '':
        print('Detected staging branch `{branch}`'
              .format(branch=environ['GITHUB_HEAD_REF']))
        upload_remote = 'trassir-staging'
    else:
        upload_remote = 'trassir-public'
    print('Will upload to {remote}'.format(remote=upload_remote))

    if 'CONAN_PASSWORD' in environ:
        if custom_remotes:
            conan_run(['user', '--password', environ['CONAN_PASSWORD'],
                       '--remote', upload_remote,
                       environ['REMOTES_UPLOAD_USER']])
        else:
            conan_run(['user', '--password', environ['CONAN_PASSWORD'],
                       '--remote', upload_remote,
                       'trassir-ci-bot'])

    return upload_remote

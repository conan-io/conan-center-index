#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import os
import subprocess
import sys

if sys.version_info[:2] < (3, 9):
    # Don't allow anything but Python 3.9 or higher
    raise SystemError('Only Python 3.9+ is allowed')

MKENV_IMPL = 'mkenv_impl'
HERE = os.path.dirname(os.path.abspath(__file__))
MKENV_SUBDIR = '.mkenv'
MKENV_REPO = os.environ.get('DL_MKENV_REPO', 'git@octocat.dlogics.com:datalogics/mkenv.git')
MKENV_BRANCH = os.environ.get('DL_MKENV_BRANCH', 'main')
DL_MKENV_ENVIRONMENT_OVERRIDE = 'DL_MKENV_REPO' in os.environ or 'DL_MKENV_BRANCH' in os.environ
# The oldest Git v2 we have on our machines is 2.3, and it seems to work for mkenv.
GIT_REQUIRED = (2, 3)


def run(command_args, verbose=False, check=True, capture_output=False, *args, **kwargs):
    if verbose:
        print(' '.join(command_args), file=sys.stderr)
    redirect_stderr = subprocess.PIPE if capture_output else None
    redirect_stdout = subprocess.PIPE if capture_output else sys.stderr
    return subprocess.run(command_args, check=check, stdout=redirect_stdout, stderr=redirect_stderr,
                          *args, **kwargs)


def get_mkenv_impl_from_git():
    old_sys_path = sys.path.copy()
    try:
        mkenv_dir = os.path.join(HERE, MKENV_SUBDIR)
        # snipe the verbose flag from the argv to decide how chatty to be about the
        # git commands
        verbose = '-v' in sys.argv or '--verbose' in sys.argv

        # Check git version
        completed = run(['git', 'version'], capture_output=True, check=True)
        git_version = completed.stdout.decode().strip().split()[2]
        # Windows has string stuff after the first three numbers, hence the [:3]
        git_version_split = [int(x) for x in git_version.split('.')[:3]]
        if tuple(git_version_split[:len(GIT_REQUIRED)]) < GIT_REQUIRED:
            ver_string = '.'.join(str(x) for x in GIT_REQUIRED)
            sys.exit(f'*** Git version {ver_string} or newer required, found {git_version}; '
                     f' older versions are no longer supported')

        if os.path.isdir(mkenv_dir) and not os.path.islink(mkenv_dir):
            # In case the repo wasn't initialized...initializing it again actually doesn't hurt anything
            run(['git', '-C', mkenv_dir, 'init'])
            completion = run(['git', '-C', mkenv_dir, 'remote', 'set-url', 'origin', MKENV_REPO], verbose=verbose,
                             check=False)
            if completion.returncode != 0:
                completion = run(['git', '-C', mkenv_dir, 'remote', 'add', 'origin', MKENV_REPO], verbose=verbose)
            run(['git', '-C', mkenv_dir, 'fetch', 'origin'], verbose=verbose)
            run(['git', '-C', mkenv_dir, 'checkout', MKENV_BRANCH], verbose=verbose)
            run(['git', '-C', mkenv_dir, 'reset', '--hard', f'origin/{MKENV_BRANCH}'], verbose=verbose)
        elif os.path.exists(mkenv_dir):
            sys.exit('*** .mkenv is not a directory; remove it and try again.')
        else:
            run(['git', 'clone', MKENV_REPO, MKENV_SUBDIR, '--branch', MKENV_BRANCH], verbose=verbose)
        sys.path.insert(0, mkenv_dir)
        mkenv_impl = importlib.import_module(MKENV_IMPL)
        return mkenv_impl
    finally:
        sys.path[:] = old_sys_path


def main():
    mkenv_impl = None

    if not DL_MKENV_ENVIRONMENT_OVERRIDE:
        # Use local module only if exists and not overridden by environment
        old_sys_path = sys.path.copy()
        sys.path.insert(0, HERE)
        try:
            mkenv_impl = importlib.import_module(MKENV_IMPL)
        except ModuleNotFoundError:
            pass
        finally:
            sys.path[:] = old_sys_path

    if mkenv_impl is None:
        mkenv_impl = get_mkenv_impl_from_git()
    return mkenv_impl.main(HERE)


if __name__ == '__main__':
    sys.exit(main())

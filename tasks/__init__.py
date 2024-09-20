# pylint: disable=all
import importlib
import io
import os
from concurrent import futures

import coloredlogs
import yaml
from dl_conan_build_tools.tasks import conan
from invoke import Collection, Exit
from invoke.tasks import Task, task

from . import merging

TASKS_FIELD_STYLES = coloredlogs.DEFAULT_FIELD_STYLES.copy()
TASKS_FIELD_STYLES.update(levelname=dict(color='magenta', bold=True))
coloredlogs.install(field_styles=TASKS_FIELD_STYLES,
                    fmt='%(asctime)s %(funcName)s %(name)s[%(process)d] %(levelname)s %(message)s')


@task(help={'remote': 'remote to upload to, default conan-center-dl-staging',
            'package': 'name of package to upload, can be specified more than once',
            'all': 'upload all packages in recipes folder',
            'since-commit': 'upload all packages in recipes folder changed since COMMIT',
            'since-before-last-merge': 'upload all packages in recipes folder changed since just before the most '
                                       'recent merge (this is useful for automated tools)',
            'since-merge-from-branch': 'upload packages changed since a merge from the given branch',
            'merges': 'number of merges to look back for since-merge-from-branch, default 2',
            'parallel': 'run uploads in parallel (default)',
            'upload': 'upload the recipe (default) (otherwise, just does the exports)'
            },
      iterable=['package'])
def upload_recipes(ctx, remote='conan-center-dl-staging', package=None, all=False, since_commit=None,
                   since_before_last_merge=False, since_merge_from_branch=None, merges=2,
                   parallel=True, upload=True):
    """Export and upload the named recipes to the given remote.

    Exports and uploads all the versions of the selected recipes to the remote."""
    packages = set()

    def update_since_commit(since_commit):
        stm = io.StringIO()
        ctx.run(f'git diff --name-only {since_commit} -- recipes', out_stream=stm, pty=False, dry=False)
        lines = stm.getvalue().strip('\n').split('\n')
        # Include the recipe if the diff mentions a file and that file still exists.
        # This avoids trying to do uploads for files that have been deleted.
        packages.update(path.split('/')[1] for path in lines if path and os.path.exists(path))

    def search_branch_merge():
        # Get all revs from branch
        stm = io.StringIO()
        ctx.run(f'git rev-list {since_merge_from_branch}', out_stream=stm, pty=False, dry=False)
        branch_revs = set(stm.getvalue().strip('\n').split('\n'))

        # Get all merges, and all their parents
        stm = io.StringIO()
        ctx.run("git log --min-parents=2 --pretty='%H %P'", out_stream=stm, pty=False, dry=False)
        merges_seen = 0
        for line in stm.getvalue().strip('\n').split('\n'):
            refs = line.split()
            merge_commit = refs[0]
            parents = refs[1:]
            if set(parents).intersection(branch_revs):
                merges_seen += 1
            if merges_seen == merges:
                return merge_commit

    packages.update(package or [])
    if all:
        packages.update(os.listdir('recipes'))
    if since_commit:
        update_since_commit(since_commit)
    if since_before_last_merge:
        stm = io.StringIO()
        # Find most recent merge commit from current HEAD, basically the first rev that has more than one parent
        # https://stackoverflow.com/a/41464631/11996393
        ctx.run('git rev-list --min-parents=2 --max-count=1 HEAD', out_stream=stm, pty=False, dry=False)
        commit = stm.getvalue().strip('\n')
        # {commit}~1 is the first parent of {commit}; see https://git-scm.com/docs/git-rev-parse#_specifying_revisions
        update_since_commit(f'{commit}~1')
    if since_merge_from_branch:
        commit = search_branch_merge()
        update_since_commit(commit)

    sorted_packages = sorted(packages)
    print('*** Uploading:')
    for pkg in sorted_packages:
        print(f'    {pkg}')

    def do_upload(one_package):
        upload_one_package_name(ctx, one_package, remote, upload=upload)

    if parallel:
        upload_in_parallel(do_upload, sorted_packages)
    else:
        for one_package in sorted_packages:
            do_upload(one_package)


def upload_in_parallel(do_upload, sorted_packages, thread_name_prefix=None):
    """Upload recipes in parallel"""
    with futures.ThreadPoolExecutor(thread_name_prefix='upload_recipes') as executor:
        future_to_package = {executor.submit(do_upload, one_package): one_package for one_package in sorted_packages}
        for future in futures.as_completed(future_to_package):
            exception = future.exception()
            if exception:
                # Fail on first problem
                executor.shutdown(wait=True, cancel_futures=True)
                one_package = future_to_package[future]
                raise Exit(f'error exporting/uploading {one_package}: {exception}') from exception


def upload_one_package_name(ctx, package_name, remote, upload=True):
    """Upload one recipe to the given remote"""
    ctx.run(f'conan remove {package_name} --force')
    recipe_folder = os.path.join('recipes', package_name)
    config_yml_file = os.path.join(recipe_folder, 'config.yml')
    if os.path.exists(config_yml_file):
        with open(config_yml_file, 'r') as config_yml:
            config_data = yaml.safe_load(config_yml)
            for version, config in config_data['versions'].items():
                folder = os.path.join(recipe_folder, config['folder'])
                ctx.run(f'conan export {folder} {package_name}/{version}@')
    else:
        with os.scandir(recipe_folder) as dirs:
            for entry in dirs:
                if not entry.name.startswith('.') and entry.is_dir():
                    version = entry.name
                    folder = os.path.join(recipe_folder, version)
                    ctx.run(f'conan export {folder} {package_name}/{version}@')
    if upload:
        # Force upload to make sure that if there has been back-and-forth changes
        # to the branch, the current recipe rises to the top of the revisions
        # sorted by date.
        ctx.run(f'conan upload -r {remote} {package_name} --force --confirm')


tasks = []
tasks.extend([v for v in locals().values() if isinstance(v, Task)])
tasks.append(merging.merge_upstream)
tasks.append(merging.merge_staging_to_production)

conan_tasks = Collection()
conan_tasks.add_task(conan.install_config)
conan_tasks.add_task(conan.login)
conan_tasks.add_task(conan.purge)

# Load the Jenkins tasks form dl_pre_commit_hooks, if it is available
# (which it is not on AIX or Solaris)
try:
    jenkins_tasks = importlib.import_module('dl_pre_commit_hooks.tasks.jenkins')
    tasks.append(jenkins_tasks)
except ModuleNotFoundError:
    pass

ns = Collection(*tasks)
ns.add_collection(conan_tasks, 'conan')

ns.configure({'run': {'echo': 'true'}})

"""Tasks and supporting functions related to merging branches."""
import contextlib
import dataclasses
import getpass
import json
import logging
import os
import platform
import shlex
import shutil
import tempfile
import textwrap
import typing
from enum import Enum, auto
from typing import Optional

import dacite
import yaml
from invoke import Exit, Task, UnexpectedExit

# Git config option to disable rerere, which tries to reuse merge conflict resolutions
DISABLE_RERERE = '-c rerere.enabled=false '

# Name of a status file
MERGE_UPSTREAM_STATUS = '.merge-upstream-status'
MERGE_STAGING_TO_PRODUCTION_STATUS = '.merge-staging-to-production-status'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MergeHadConflicts(Exception):
    """Thrown when the merge had conflicts. Usually handled by making a pull request."""

    def __init__(self, conflicts=None):
        """
        Create the exception, with optional list of conflicts.

        @param conflicts: a list of conflicts that were found
        """
        self.conflicts = conflicts


class MergeStatus(Enum):
    """The status of the attempted merge. The name of this status will be placed into the
    file .merge-upstream-status."""
    UP_TO_DATE = auto()
    """The branch was already up to date."""
    MERGED = auto()
    """The branch was merged (and pushed)."""
    PULL_REQUEST = auto()
    """A pull request was necessary."""


@dataclasses.dataclass
class ConanCenterIndexConfig:
    """Configuration for Conan Center Index"""
    url: str = 'git@github.com:conan-io/conan-center-index.git'
    """URL for the Conan Center Index"""
    branch: str = 'master'
    """Branch to fetch from"""


@dataclasses.dataclass
class UpstreamConfig:
    """Configuration describing parameters for the upstream repo. (usually Datalogics)"""
    host: str = 'octocat.dlogics.com'
    """Host for the Datalogics upstream"""
    organization: str = 'datalogics'
    """Name of the upstream organization"""
    branch: str = 'develop'
    """Name of the branch that Conan Center Index is merged to"""
    remote_name: str = 'merge-upstream-remote'
    """Name of a temporary remote to create to do the work"""

    @property
    def url(self) -> str:
        """The URL for the upstream Git repository."""
        return f'git@{self.host}:{self.organization}/conan-center-index.git'


@dataclasses.dataclass
class PullRequestConfig:
    """Configuration describing parameters for the pull request"""
    host: str = 'octocat.dlogics.com'
    """Host for the pull request"""
    fork: str = getpass.getuser()
    """The fork to create the pull request on."""
    merge_branch_name: str = 'merge-from-conan-io'
    """The name of the head branch to create"""
    reviewers: list[str] = dataclasses.field(default_factory=list)
    """A list of usernames from which to request reviews"""
    assignee: Optional[str] = None
    """A username to be the assignee"""
    labels: list[str] = dataclasses.field(default_factory=lambda: ['from-conan-io'])
    """Labels to place on the pull request"""

    @property
    def url(self) -> str:
        """Return the URL to push to for the pull request."""
        return f'git@{self.host}:{self.fork}/conan-center-index.git'


class Config:
    """Base class for Config dataclasses that read from dlproject.yaml"""
    yaml_key = None

    class ConfigurationError(Exception):
        """Configuration error when reading data."""

    @classmethod
    def _check_attributes(cls):
        if cls.yaml_key is None:
            raise NotImplementedError(f"Class {cls.__name__} must define 'yaml_key' as a 'ClassVar[str]' \n"
                                      '    which indicates the key for the config in dlproject.yaml.')

    @classmethod
    def create_from_dlproject(cls):
        """Create an instance of cls with defaults updated from dlproject.yaml"""
        cls._check_attributes()
        with open('dlproject.yaml', encoding='utf-8') as dlproject_file:
            dlproject = yaml.safe_load(dlproject_file)
        config_data = dlproject.get(cls.yaml_key, {})
        # If dlproject.yaml has an empty key, then the config_data will be None,
        # and it won't get replaced by the empty dict. Check for that.
        if config_data is None:
            config_data = {}
        try:
            return dacite.from_dict(data_class=cls,
                                    data=config_data,
                                    config=dacite.Config(strict=True))
        except dacite.DaciteError as exception:
            raise cls.ConfigurationError(
                f'Error reading {cls.yaml_key} from dlproject.yaml: {exception}') from exception

    def asyaml(self):
        """Return a string containing the yaml for this dataclass,
        in canonical form."""
        self._check_attributes()
        # sort_keys=False to preserve the ordering that's in the dataclasses
        # dict objects preserve order since Python 3.7
        return yaml.dump({self.yaml_key: dataclasses.asdict(self)}, sort_keys=False, indent=4)


@dataclasses.dataclass
class MergeUpstreamConfig(Config):
    """Configuration for the merge-upstream task."""
    cci: ConanCenterIndexConfig = dataclasses.field(default_factory=ConanCenterIndexConfig)
    """Configuration for Conan Center Index"""
    upstream: UpstreamConfig = dataclasses.field(default_factory=UpstreamConfig)
    """Configuration for the Datalogics upstream"""
    pull_request: PullRequestConfig = dataclasses.field(default_factory=PullRequestConfig)
    """Configuration for the pull request"""
    yaml_key: typing.ClassVar[str] = 'merge_upstream'
    """Key for this configuration in dlproject.yaml."""


@dataclasses.dataclass
class MergeStagingToProductionConfig(Config):
    """Configuration describing parameters for production merges in the upstream repo. (usually Datalogics)"""
    host: str = 'octocat.dlogics.com'
    """Host for the Datalogics upstream"""
    organization: str = 'datalogics'
    """Name of the upstream organization"""
    staging_branch: str = 'develop'
    """Name of the staging branch"""
    production_branch: str = 'master'
    """Name of the production branch"""
    yaml_key: typing.ClassVar[str] = 'merge_staging_to_production'
    """Key for this configuration in dlproject.yaml."""

    @property
    def url(self) -> str:
        """The URL for the upstream Git repository."""
        return f'git@{self.host}:{self.organization}/conan-center-index.git'


@dataclasses.dataclass
class GitFileStatus:
    """A Git status"""
    status: str
    """A Git short status string, see https://git-scm.com/docs/git-status#_short_format"""
    path: str
    """A file path, which may be two paths separated by -> if a rename or copy"""
    merge_attr: str = 'unspecified'
    """The merge attribute for this path from .gitattributes"""


@Task
def merge_upstream(ctx):
    '''Merge updated recipes and other files from conan-io/conan-center-index.

    If the merge does not succeed, it will open a pull request against the destination
    repository, assigning the PR, and requesting reviewers.

    To make a file always keep DL's version in a merge, add it to .gitattributes-merge
    with the attribute merge=ours.
    '''
    config = MergeUpstreamConfig.create_from_dlproject()
    _check_preconditions(ctx, config)
    logger.info('merge-upstream configuration:\n%s', config.asyaml())

    # if anything fails past this point, the missing status file will also abort the Jenkins run.
    _remove_status_file(MERGE_UPSTREAM_STATUS)
    # Nested context handlers; see https://docs.python.org/3.10/reference/compound_stmts.html#the-with-statement
    with _preserving_branch_and_commit(ctx), _merge_remote(ctx, config):
        # Try to merge from CCI
        try:
            _write_status_file(_merge_and_push(ctx, config), to_file=MERGE_UPSTREAM_STATUS)
        except MergeHadConflicts as merge_exception:
            try:
                pr_body = _form_pr_body(ctx, config, merge_exception.conflicts)
            finally:
                ctx.run('git merge --abort')
            _create_pull_request(ctx, config, pr_body, merge_exception.conflicts)
            _write_status_file(MergeStatus.PULL_REQUEST, to_file=MERGE_UPSTREAM_STATUS)


@Task
def merge_staging_to_production(ctx):
    """Merge the staging branch to the production branch"""
    config = MergeStagingToProductionConfig.create_from_dlproject()
    logger.info('merge-staging-to-production configuration:\n%s', config.asyaml())
    with _preserving_branch_and_commit(ctx):
        _remove_status_file(MERGE_STAGING_TO_PRODUCTION_STATUS)
        logger.info('Check out production branch...')
        ctx.run(f'git fetch {config.url} {config.production_branch}')
        ctx.run('git checkout --detach FETCH_HEAD')

        logger.info('Merge staging branch...')
        ctx.run(f'git fetch {config.url} {config.staging_branch}')
        if _count_revs(ctx, 'HEAD..FETCH_HEAD') == 0:
            logger.info('%s is up to date.', config.production_branch)
            _write_status_file(MergeStatus.UP_TO_DATE, to_file=MERGE_STAGING_TO_PRODUCTION_STATUS)
            return
        ctx.run(
            f'git {DISABLE_RERERE} merge --no-ff --no-edit --no-verify --into-name '
            f'{config.production_branch} FETCH_HEAD')

        logger.info('Push merged production branch...')
        ctx.run(f'git push {config.url} HEAD:refs/heads/{config.production_branch}')
        _write_status_file(MergeStatus.MERGED, to_file=MERGE_STAGING_TO_PRODUCTION_STATUS)


def _remove_status_file(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


def _write_status_file(merge_status, to_file):
    """Write the merge status to the status file."""
    logger.info('Write status %s to file %s', merge_status.name, to_file)
    with open(to_file, 'w', encoding='utf-8') as status:
        status.write(merge_status.name)


@contextlib.contextmanager
def _preserving_branch_and_commit(ctx):
    """Context manager to run complicated sets of Git commands, while returning
    to the original branch and placing that branch back onto the original commit."""
    logger.info('Save current checkout state...')
    result = ctx.run('git rev-parse --abbrev-ref HEAD', hide='stdout')
    branch = result.stdout.strip()
    result = ctx.run('git rev-parse HEAD', hide='stdout')
    commit = result.stdout.strip()
    try:
        yield
    finally:
        logger.info('Restore checkout state...')
        if branch == 'HEAD':
            ctx.run(f'git checkout --quiet --detach {commit}')
            ctx.run('git reset --hard HEAD')
        else:
            ctx.run(f'git checkout --quiet --force {branch}')
            ctx.run(f'git reset --hard {commit}')


def _check_preconditions(ctx, config):
    """Check the preconditions for the merge-upstream task."""
    logger.info('Check preconditions...')
    if platform.system() not in ['Darwin', 'Linux']:
        raise Exit('Run this task on macOS or Linux')
    # https://stackoverflow.com/a/2659808/11996393
    result = ctx.run('git diff-index --quiet HEAD --', warn=True, hide='stdout')
    if not result.ok:
        raise Exit('The local worktree has uncommitted changes')
    if not shutil.which('gh'):
        raise Exit('This task requires the GitHub CLI. See installation instructions at https://cli.github.com/')
    result = ctx.run(f'gh auth status --hostname {config.upstream.host}', warn=True)
    if not result.ok:
        raise Exit(f'GitHub CLI must be logged in to {config.upstream.host}, or a token supplied in GH_TOKEN; '
                   f'see https://cli.github.com/manual/gh_auth_login')


@contextlib.contextmanager
def _merge_remote(ctx, config):
    '''Make merge-local-remote point to the repo we're going to merge into
    This also makes it work in CI, where there might not be an "upstream".

    Used as a context manager, cleans up the remote when done.'''
    try:
        logger.info('Create remote to refer to destination fork...')
        result = ctx.run(f'git remote get-url {config.upstream.remote_name}', hide='both', warn=True, pty=False)
        if result.ok and result.stdout.strip() != '':
            ctx.run(f'git remote set-url {config.upstream.remote_name} {config.upstream.url}')
        else:
            ctx.run(f'git remote add {config.upstream.remote_name} {config.upstream.url}')
        ctx.run(f'git remote update {config.upstream.remote_name}')
        yield
    finally:
        logger.info('Remove remote...')
        ctx.run(f'git remote remove {config.upstream.remote_name}', warn=True, hide='both')


def _branch_exists(ctx, branch):
    """Return true if the given branch exists locally"""
    logger.info('Check if %s exists...', branch)
    result = ctx.run(f'git rev-parse --quiet --verify {branch}', warn=True, hide='stdout')
    return result.ok


def _count_revs(ctx, commit):
    """Count the revisions in the given commit, which can be a range like branch..HEAD, or
    other commit expression."""
    count_revs_result = ctx.run(f'git rev-list {commit} --count', hide='stdout', pty=False)
    return int(count_revs_result.stdout)


def _merge_and_push(ctx, config):
    """Attempt to merge upstream branch and push it to the local repo."""
    logger.info('Check out local %s branch...', config.upstream.branch)
    ctx.run(f'git checkout --quiet --detach {config.upstream.remote_name}/{config.upstream.branch}')
    logger.info('Merge upstream branch...')
    ctx.run(f'git fetch {config.cci.url} {config.cci.branch}')
    # --into name sets the branch name so it says "...into develop" instead of "...into HEAD"
    # Have to fetch and use FETCH_HEAD because --into-name isn't available on git pull
    #
    # For files in .gitattributes-merge that have merge=ours, resolve in favor of
    # our changes. These files have been "taken over" from GitHub.
    merge_result = ctx.run(
        'git '
        # Add the attributes in .gitattributes-merge to the list of attributes,
        # see https://www.git-scm.com/docs/git-config#Documentation/git-config.txt-coreattributesFile
        '-c core.attributesFile=.gitattributes-merge '
        # Add a custom merge driver 'ours' which keeps just the file on HEAD, favoring
        # our version of those files.
        # See the section "Merge Strategies" at the end of
        # https://www.git-scm.com/book/en/v2/Customizing-Git-Git-Attributes
        '-c merge.ours.driver=true '
        f'{DISABLE_RERERE} '
        f'merge --no-ff --no-edit --no-verify --into-name {config.upstream.branch} FETCH_HEAD',
        warn=True)
    if merge_result.ok:
        return _maybe_push(ctx, config)
    original_conflicts = _retrieve_merge_conflicts(ctx)
    if not original_conflicts:
        # Something else went wrong with the merge
        raise UnexpectedExit(merge_result)
    _remove_files_deleted_by_us(ctx, original_conflicts)
    conflicts = _retrieve_merge_conflicts(ctx)
    if conflicts:
        # There are still unresolved conflicts. Raise an exception,
        # and the top level PR will turn it into a pull request.
        _raise_exception_for_conflicted_merge(ctx)
    logger.info('Commit merge with resolved conflicts...')
    # Finish the merge by committing. --no-verify is necessary to avoid running commit
    # hooks, which aren't run on merge commits that succeed.
    ctx.run('git commit --no-edit --no-verify')
    return _maybe_push(ctx, config)


def _raise_exception_for_conflicted_merge(ctx):
    """Redo the merge to get the complete list of conflicts, without the 'ours' merge
    driver. Then, raise the MergeHadConflicts exception with the complete list."""
    # Redo the merge to get all the conflicts, including the ones we resolve as 'ours'
    logger.info('Redoing merge to get complete conflict list')
    ctx.run('git merge --abort')
    ctx.run(f'git {DISABLE_RERERE} merge --no-commit --no-ff FETCH_HEAD', warn=True)
    conflicts = _retrieve_merge_conflicts(ctx)
    conflicts = _find_merge_attributes(ctx, conflicts)
    raise MergeHadConflicts(conflicts)


def _remove_files_deleted_by_us(ctx, conflicts):
    """Examine conflicts for files deleted by us (status DU) and remove them with 'git rm'.
    This may clear enough of the conflicts to allow auto-merging to continue."""
    logger.info('Removing conflict files deleted by us...')
    paths = [conflict.path for conflict in conflicts if conflict.status == 'DU']
    for path in paths:
        ctx.run(f'git rm {path}')
    return paths


def _retrieve_merge_conflicts(ctx):
    """Get a list of merge conflicts, from the current status.
    Returns a tuple of (code, path), where code is a combination
    of D (deleted) A (added) and U (unmerged).

    DD: unmerged, both deleted
    AU: unmerged, added by us
    UD: unmerged, deleted by them
    UA: unmerged, added by them
    DU: unmerged, deleted by us
    AA: unmerged, both added
    UU: unmerged, both modified

    See: https://git-scm.com/docs/git-status#_short_format"""
    logger.info('Check for merge conflicts...')
    result = ctx.run('git status --porcelain=v1', pty=False, hide='stdout')
    status_entries = [GitFileStatus(*line.split(maxsplit=1)) for line in result.stdout.splitlines()]
    conflict_statuses = {'DD', 'AU', 'UD', 'UA', 'DU', 'AA', 'UU'}
    return [entry for entry in status_entries if entry.status in conflict_statuses]


def _maybe_push(ctx, config):
    """Check to see if a push is necessary by counting the number of revisions
    that differ between current head and the push destination. Push if necessary"""

    if _count_revs(ctx, f'{config.upstream.remote_name}/{config.upstream.branch}..HEAD') == 0:
        logger.info('Repo is already up to date')
        return MergeStatus.UP_TO_DATE
    logger.info('Push to local repo...')
    ctx.run(f'git push {config.upstream.remote_name} HEAD:refs/heads/{config.upstream.branch}')
    return MergeStatus.MERGED


def _find_merge_attributes(ctx, conflicts):
    """Find the merge attributes for the conflicts"""
    modify_conflicts = [conflict.path for conflict in conflicts if conflict.status == 'UU']
    check_attr = ctx.run(
        f'git -c core.attributesFile=.gitattributes-merge check-attr merge -z -- {" ".join(modify_conflicts)}',
        hide='stdout', pty=False)
    # The -z means data fields separated by NUL
    check_attr_data = check_attr.stdout.strip('\0').split('\0')
    # Iterate in groups of three
    # https://stackoverflow.com/a/18541496/11996393
    check_attr_iters = [iter(check_attr_data)] * 3
    path_attrs = {path: value for path, _, value in zip(*check_attr_iters)}
    new_conflicts = [dataclasses.replace(conflict, merge_attr=path_attrs.get(conflict.path, 'unspecified'))
                     for conflict in conflicts]
    return new_conflicts


def _unresolvable_conflicts(conflicts):
    """Filter the conflict list, returning the ones that are unresolvable"""

    def resolvable(conflict):
        # DU conflicts (Datalogics deleted, conan-io modified) are resolvable
        if conflict.status == 'DU':
            return True
        # merge=ours conflicts are resolvable
        if conflict.status == 'UU' and conflict.merge_attr == 'ours':
            return True
        return False

    return [conflict for conflict in conflicts if not resolvable(conflict)]


def _form_pr_body(ctx, config, conflicts):
    """Create a body for the pull request summarizing information about the merge conflicts."""
    # Note: pty=False to enforce not using a PTY; that makes sure that Git doesn't
    # see a terminal and put escapes into the output we want to format.
    logger.info('Create body of pull request message...')
    files = [conflict.path for conflict in _unresolvable_conflicts(conflicts)]
    files_arg = ' '.join(files)
    commits_on_upstream_result = ctx.run(
        f'git log --no-color --no-merges --merge HEAD..MERGE_HEAD --pretty=format:"%h - %s (%cr) <%an>" -- {files_arg}',
        hide='stdout', pty=False)
    # Get the paths of only the unresolvable conflicts
    # Note: 'git diff HEAD...MERGE_HEAD' is a diff of changes on MERGE_HEAD that are not on HEAD.
    # It's the same as: git diff $(git merge-base HEAD MERGE_HEAD) MERGE_HEAD
    # See: https://git-scm.com/docs/git-diff for more details
    diff_on_upstream_result = ctx.run(f'git diff -U HEAD...MERGE_HEAD -- {files_arg}', hide='stdout', pty=False)
    commits_local_result = ctx.run(
        f'git log --no-color --no-merges --merge MERGE_HEAD..HEAD --pretty=format:"%h - %s (%cr) <%an>" -- {files_arg}',
        hide='stdout', pty=False)
    diff_on_local_result = ctx.run(f'git diff -U MERGE_HEAD...HEAD -- {files_arg}', hide='stdout', pty=False)
    body = textwrap.dedent('''
        Merge changes from conan-io/conan-center-index into {local_branch}.

        This PR was automatically created due to merge conflicts in the automated merge.

        ## Conflict information

        ### List of conflict files

        {conflict_files}

        ### Commits for conflict files on `conan-io`

        {commits_on_upstream}

        #### Differences on `conan-io`

        <details><summary>Click to reveal...</summary>

        ```diff
        {diff_on_upstream}
        ```

        </details>

        ### Commits for conflict files, local

        {commits_local}

        #### Differences, local

        <details><summary>Click to reveal...</summary>

        ```diff
        {diff_on_local}
        ```

        </details>

    ''').format(local_branch=config.upstream.branch,
                conflict_files='\n'.join(files),
                commits_on_upstream=commits_on_upstream_result.stdout,
                diff_on_upstream=diff_on_upstream_result.stdout,
                commits_local=commits_local_result.stdout,
                diff_on_local=diff_on_local_result.stdout)

    return body


def _create_pull_request(ctx, config, pr_body, conflicts):
    """Create a pull request to merge in the data from upstream."""
    logger.info('Create pull request from upstream branch...')
    # Get the upstream ref
    ctx.run(f'git fetch {config.cci.url} {config.cci.branch}')
    ctx.run('git checkout --detach FETCH_HEAD')

    # Remove files that DL deleted, but were modified by conan-io
    if _remove_files_deleted_by_us(ctx, conflicts):
        ctx.run('git commit --no-verify -m "Delete conflicting files that were deleted by DL"')

    # Resolve files in our favor if they have the attribute merge=ours
    merge_ours = [conflict.path for conflict in conflicts if conflict.status == 'UU' and conflict.merge_attr == 'ours']
    if merge_ours:
        for path in merge_ours:
            ctx.run(f'git checkout {config.upstream.remote_name}/{config.upstream.branch} -- {path}')
        ctx.run('git commit --no-verify -m "Favor DL changes for files where merge=ours"')

    # Push it to the fork the PR will be on. Have to include refs/heads in case the branch didn't
    # already exist
    ctx.run(f'git push --force {config.pull_request.url} '
            f'HEAD:refs/heads/{config.pull_request.merge_branch_name}')
    with tempfile.NamedTemporaryFile(prefix='pr-body', mode='w+', encoding='utf-8') as pr_body_file:
        pr_body_file.write(pr_body)
        # Before passing the filename to gh pr create, flush it so all the data is on the disk
        pr_body_file.flush()

        existing_prs = _list_merge_pull_requests(ctx, config)
        if existing_prs:
            assert len(existing_prs) == 1
            url = existing_prs[0]['url']
            logger.info('Edit existing pull request...')
            ctx.run(f'gh pr edit --repo {config.upstream.host}/{config.upstream.organization}/conan-center-index '
                    f'{url} --body-file {pr_body_file.name}')
        else:
            logger.info('Create new pull request...')
            title = shlex.quote('Merge in changes from conan-io/master')
            labels = f' --label {",".join(config.pull_request.labels)}' if config.pull_request.labels else ''
            assignee = f' --assignee {config.pull_request.assignee}' if config.pull_request.assignee else ''
            reviewer = f' --reviewer {",".join(config.pull_request.reviewers)}' if config.pull_request.reviewers else ''
            ctx.run(f'gh pr create --repo {config.upstream.host}/{config.upstream.organization}/conan-center-index '
                    f'--base {config.upstream.branch} '
                    f'--title {title} --body-file {pr_body_file.name} '
                    f'--head {config.pull_request.fork}:{config.pull_request.merge_branch_name}'
                    f'{labels}{assignee}{reviewer}')


def _list_merge_pull_requests(ctx, config):
    logger.info('Check for existing pull requests...')
    result = ctx.run(f'gh pr list --repo {config.upstream.host}/{config.upstream.organization}/conan-center-index '
                     '--json number,url,author,headRefName,headRepositoryOwner ',
                     hide='stdout',
                     pty=False)
    out = result.stdout.strip()
    requests = json.loads(out) if out else []
    branch_name = config.pull_request.merge_branch_name
    fork = config.pull_request.fork
    return [r for r in requests if r['headRefName'] == branch_name and r['headRepositoryOwner']['login'] == fork]

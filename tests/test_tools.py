import collections.abc
import itertools
import json
import os
import platform
import shutil
import subprocess
from typing import List, NamedTuple

import dl_conan_build_tools.config
import pytest
import semver
from dl_conan_build_tools.tasks.conan import Config

from util import recipes

_config = dl_conan_build_tools.config.get_config()


class Package(NamedTuple):
    package: str
    options: List[str] = list()
    configs: List[str] = list()
    recipe_from: str = None

    def __str__(self):
        result = self.package
        if self.options:
            result = f'{self.package}_{"_".join(self.options)}'
        return result

    @classmethod
    def from_str_or_dict(cls, str_or_dict):
        """Create a package from a string or dict."""
        if isinstance(str_or_dict, str):
            return cls(str_or_dict, [])
        return cls(**str_or_dict)

    @classmethod
    def create_resolved(cls, str_or_dict):
        """Create a package from a string or dict, and resolve ranges."""
        return cls.from_str_or_dict(str_or_dict).resolve_ranges()

    def resolve_ranges(self):
        """Check if the package has a range expression, and resolve it if necessary."""
        package, range = self.package.split('/', maxsplit=1)
        if range.startswith('[') and range.endswith(']'):
            if self.recipe_from:
                versions = recipes.conandata_versions(self.recipe_from)
            else:
                versions = recipes.versions_to_folders(package).keys()
            range = range[1:-1]  # strip off brackets
            # Could call conans.client.graph.range_resolver.satisfying() here, but
            # avoiding using Conan internals. That means not supporting loose or include_prerelease
            # for now. In Conan, loose is the default.
            resolved_version = semver.max_satisfying(versions, range, loose=True, include_prerelease=False)
            if resolved_version is None:
                print(f'*** No range resolution for {self.package}')
                return self
            resolved_package = f'{package}/{resolved_version}'
            print(f'Resolved {self.package} to {resolved_package}')
            return Package(resolved_package, self.options, self.configs, recipe_from=self.recipe_from)
        else:
            return self


def config_from_name(config_name):
    config = Config.from_name(config_name)
    config.validate()
    config = config.normalize()

    config.infer_additional_configuration()

    return config


class ConfiguredPackage(NamedTuple):
    """A configured package, combining the package with its configuration"""
    package: Package
    config_name: str
    config: Config

    def __str__(self):
        return f'{self.package}-{self.config_name}'


def _tools_and_configs():
    """Return tuples of prebuilt_tool, config, and config_name, by taking the Cartesian product
     of the tools and configs, and filtering out the configs that don't apply."""
    prebuilt_tools = (Package.create_resolved(entry) for entry in _config.get('prebuilt_tools', []))
    configs = ((config_name, config_from_name(config_name)) for config_name in
               _config.get('prebuilt_tools_configs', []))
    return [ConfiguredPackage(tool, config_name, config)
            for tool, (config_name, config) in itertools.product(prebuilt_tools, configs)
            if not tool.configs or config_name in tool.configs]


@pytest.fixture(scope='package',
                params=_tools_and_configs(),
                ids=lambda param: str(param))
def tool_and_config(request):
    return request.param


@pytest.fixture(scope='package')
def release_tool_config():
    return config_from_name('ReleaseTool')


@pytest.fixture(scope='package')
def tool_recipe_folder(tool_and_config):
    prebuilt_tool = tool_and_config.package
    if prebuilt_tool.recipe_from:
        return prebuilt_tool.recipe_from
    package, version = prebuilt_tool.package.split('/')
    return recipes.versions_to_folders(package).get(version)


@pytest.fixture(scope='package')
def msys_env(release_tool_config, tmpdir_factory, upload_to):
    if platform.system() == 'Windows' and platform.machine().lower() != 'arm64':
        msys2_dir = tmpdir_factory.mktemp('msys2_install')
        install_json = msys2_dir / 'install.json'
        args = ['conan', 'install', '--update', 'msys2/cci.latest@', '-if', msys2_dir, '-g', 'json',
                '--build', 'missing', '-j', install_json]
        args.extend(release_tool_config.install_options())
        subprocess.run(args, check=True)

        # Upload msys2 if it was built, since it should still be clean
        with open(install_json, 'r') as json_file:
            install_data = json.load(json_file)
        for install in install_data['installed']:
            recipe_id = install['recipe']['id']
            ref = recipe_id.split('#')[0]
            package = ref.split('/')[0]
            if package == 'msys2':
                built = False
                for package in install['packages']:
                    built = built or package['built']
                if built and upload_to:
                    args = ['conan', 'upload', '-r', upload_to, f'{ref}@', '--all', '--check']
                    print(f'Uploading {ref}: {" ".join(args)}')
                    subprocess.run(args, check=True, stderr=subprocess.STDOUT)

        with open(msys2_dir / 'conanbuildinfo.json', 'r') as json_file:
            conanbuildinfo = json.load(json_file)
            return conanbuildinfo['deps_env_info']


@pytest.fixture(scope='package')
def msys_bin(msys_env):
    """Return the value of MSYS_BIN from the msys2 package, or None if not on Windows"""
    return (msys_env or {}).get('MSYS_BIN')


@pytest.fixture(scope='package')
def conan_env(msys_bin):
    """Create an environment with extra variables for running Conan. This may include
    setting a path to MSYS2 bash so that Conan doesn't try hooking into WSL (if installed)."""
    env = os.environ.copy()
    if msys_bin:
        # It turns out that there's really no workaround that works with WSL2 installed;
        # see the discussion at https://github.com/conan-io/conan-center-index/issues/7944
        # Either autoconf doesn't build (without CONAN_BASH_PATH) or its test_package doesn't
        # build (with CONAN_BASH_PATH), so maybe the best solution is to inform the user that
        # WSL2 should not be enabled.
        # env['CONAN_BASH_PATH'] = os.path.join(msys_bin, 'bash.exe')
        bash = (shutil.which('bash') or '').lower()
        assert bash != r'c:\windows\system32\bash.exe', "Building on Windows doesn't work with WSL2 installed"
    return env


class TestBuildTools(object):
    def search_local_packages(self, ref, conan_env, tmp_path):
        search_json = tmp_path / 'search.json'
        args = ['conan', 'search', f'{ref}@', '-j', str(search_json)]
        print(f'Getting package information for {ref}: {" ".join(args)}')
        subprocess.run(args, check=True, stderr=subprocess.STDOUT, env=conan_env)
        with open(search_json) as json_file:
            search_data = json.load(json_file)
        assert search_data['results'], 'there should have been results'
        results = search_data['results']
        assert results[0]['items'], 'there should have been an item in the results'
        items = results[0]['items'][0]
        # Note: checking for key, because it is ok for this function to return an empty package list.
        # Using abstract base class to check that something is a mapping (it might not subclass
        # dict): https://stackoverflow.com/a/1278070/11996393
        assert isinstance(items, collections.abc.Mapping)
        assert 'packages' in items, 'there should have been an package list in the first item'
        return items['packages']

    def test_build_tool(self, tool_and_config, tool_recipe_folder, upload_to, force_build, tmp_path, conan_env):
        prebuilt_tool = tool_and_config.package
        prebuilt_tool_config = tool_and_config.config

        package_name, package_version = prebuilt_tool.package.split('/', maxsplit=1)
        assert not package_version.startswith('[') and not package_version.endswith(']'), 'version range must have ' \
                                                                                          'been resolved'
        assert tool_recipe_folder is not None, 'the recipe folder must be found'

        # To prevent problems with test_package build directory detritus interfering with the tests,
        # clean the recipe directory before running conan create
        args = ['git', 'clean', '-fdx', tool_recipe_folder]
        print(f'Cleaning recipe directory {tool_recipe_folder}...')
        subprocess.run(args, check=True, env=conan_env)

        tool_options = []
        for opt in prebuilt_tool.options:
            tool_options.append('--options:host')
            tool_options.append(opt)
        force_build_options = []

        if force_build == 'package':
            force_build_options = ['--build', package_name,
                                   '--build', 'missing']
        elif force_build == 'with-requirements':
            force_build_options = ['--build', '*']
            if package_name != 'cmake':
                force_build_options += ['--build', '!cmake']
        else:
            force_build_options = ['--build', 'missing']

        # Remove "missing" from the build list in the config, because it sets policy; the policy is determined by the
        # force_build_options
        config_build_without_missing = [build for build in prebuilt_tool_config.build if build != 'missing']
        config = prebuilt_tool_config._replace(build=config_build_without_missing)

        create_json = tmp_path / 'create.json'
        args = ['conan', 'create', tool_recipe_folder, f'{prebuilt_tool.package}@', '--update', '--json',
                str(create_json)] + config.install_options() + tool_options + force_build_options
        print(f'Creating package {prebuilt_tool.package}: {" ".join(args)}')
        subprocess.run(args, check=True, stderr=subprocess.STDOUT, env=conan_env)
        if upload_to:
            # upload packages mentioned in the create.json, which includes requirements used to build
            # this package, if in fact it had to be built.
            with open(create_json) as json_file:
                create_data = json.load(json_file)
            for install in create_data['installed']:
                recipe_id = install['recipe']['id']
                ref = recipe_id.split('#')[0]
                package = ref.split('/')[0]
                if package == 'msys2':
                    print(f'Not uploading {ref}, because it tends to modify itself during use.')
                    continue
                packages = self.search_local_packages(ref, conan_env, tmp_path)
                if not packages:
                    print(f'Not uploading {ref} because there are no local packages')
                    continue
                settings = packages[0].get('settings', {})
                if platform.system() == 'Windows' and 'os' not in settings:
                    # Don't upload OS-universal packages from Windows; this avoids packaging
                    # script-based packages like autoconf without the proper mode bits
                    print(f'Not uploading {ref} on Windows, because it is not os-specific.')
                    continue
                args = ['conan', 'upload', '-r', upload_to, f'{ref}@', '--all', '--check']
                print(f'Uploading {ref}: {" ".join(args)}')
                subprocess.run(args, check=True, stderr=subprocess.STDOUT, env=conan_env)

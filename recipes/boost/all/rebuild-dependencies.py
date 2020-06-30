import argparse
import dataclasses
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Dict, List

from conans import tools
import json
import yaml


BOOST_GIT_URL = "https://github.com/boostorg/boost.git"


@dataclasses.dataclass
class BoostDependencies(object):
    version: str
    buildables: List[str]
    dependencies: Dict[str, List[str]] = dataclasses.field(default_factory=dict)
    libs: Dict[str, List[str]] = dataclasses.field(default_factory=dict)


class BoostDependencyBuilder(object):
    def __init__(self, boost_version: str, boostdep_version: str, tmppath: Path, git_url: str, outputdir: Path):
        self.boost_version = boost_version
        self.boostdep_version = boostdep_version
        self.git_url = git_url
        self.tmppath = tmppath
        self.outputdir = outputdir

    @property
    def boost_path(self) -> Path:
        return self.tmppath / "boost"

    def do_git_update(self) -> None:
        if not self.boost_path.exists():
            with tools.chdir(str(self.tmppath)):
                print("Cloning boost git")
                subprocess.check_call(["git", "clone", "--", self.git_url, "boost"])
            with tools.chdir(str(self.boost_path)):
                print("Checking out current master")
                subprocess.check_call(["git checkout", "origin/master"])
                print("Removing master branch")
                subprocess.check_call(["git", "branch", "-D", "master"])
        else:
            with tools.chdir(str(self.boost_path)):
                print("Updating git repo")
                subprocess.check_call(["git", "fetch", "origin"])
                print("Removing all local changes to git repo")
                subprocess.check_call(["git", "reset", "--hard", "HEAD"])
                print("Checking out current master")
                subprocess.check_call(["git", "checkout", "origin/master"])

    def do_git_submodule_update(self):
        with tools.chdir(str(self.boost_path)):
            try:
                print("Checking out version {}".format(self.boost_version))
                subprocess.check_call(["git", "checkout", "boost-{}".format(self.boost_version)])
            except subprocess.CalledProcessError:
                print("version {} does not exist".format(self.boost_version))
                raise

            print("Initializing git submodules")
            subprocess.check_call(["git", "submodule", "update", "--init"])

    def do_install_boostdep(self):
        with tools.chdir(str(self.boost_path)):
            print("Installing boostdep/{}".format(self.boostdep_version))
            subprocess.check_call(["conan", "install", "boostdep/{}@".format(self.boostdep_version), "-g", "json"])

    @property
    def _bin_paths(self):
        with tools.chdir(str(self.boost_path)):
            data = json.loads(open("conanbuildinfo.json").read())
            return data["dependencies"][0]["bin_paths"]

    def do_boostdep_collect(self) -> BoostDependencies:
        with tools.chdir(str(self.boost_path)):
            with tools.environment_append({"PATH": self._bin_paths}):
                buildables = subprocess.check_output(["boostdep", "--list-buildable"])
                buildables = buildables.decode().splitlines()

                modules = subprocess.check_output(["boostdep", "--list-modules"])
                modules = modules.decode().splitlines()

                dep_modules = buildables

                dependency_tree = {}
                for module in dep_modules:
                    module_ts_output = subprocess.check_output(["boostdep", "--track-sources", module])
                    mod_deps = re.findall("\n([A-Za-z_-]+):\n", module_ts_output.decode())
                    dependency_tree[module] = mod_deps

        # filtered_dependency_tree = {k: [d for d in v if d in buildables] for k, v in dependency_tree.items() if k in buildables}
        boost_dependencies = BoostDependencies(dependencies=dependency_tree, buildables=buildables, version=self.boost_version)

        return boost_dependencies

    @staticmethod
    def _boostify_libraries(libs: List[str]) -> List[str]:
        return ["boost_{}".format(l) for l in libs]

    def do_create_libraries(self, boost_dependencies: BoostDependencies):
        libraries = {b: self._boostify_libraries([b]) for b in boost_dependencies.buildables}
        if "log" in libraries:
            libraries["log"] += self._boostify_libraries(["log_setup"])
        if "math" in libraries:
            libraries["math"] = self._boostify_libraries(["math_c99f", "math_c99l", "math_c99", "math_tr1f", "math_tr1l", "math_tr1"])
        if "serialization" in libraries:
            libraries["serialization"] = self._boostify_libraries(["serialization", "wserialization"])
        if "stacktrace" in libraries:
            libraries["stacktrace"] = self._boostify_libraries(["stacktrace", "stacktrace_noop", "stacktrace_backtrace", "stacktrace_addr2line", "stacktrace_basic", "stacktrace_windbg", "stacktrace_windbg_cached"])
        if "test" in libraries:
            libraries["test"] = self._boostify_libraries(["unit_test_framework", "prg_exec_monitor", "test_exec_monitor"])

        boost_dependencies.libs = libraries

        return boost_dependencies

    @property
    def _outputpath(self) -> Path:
        return self.outputdir / "dependencies-{}.yml".format(self.boost_version)

    def do_create_dependency_file(self) -> None:
        tree = self.do_boostdep_collect()
        tree = self.do_create_libraries(tree)

        data = dataclasses.asdict(tree)

        print("Creating {}".format(self.outputdir))
        with self._outputpath.open("w") as fout:
            yaml.dump(data, fout)


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", dest="tmppath", help="temporary folder where to clone boost")
    parser.add_argument("-d", dest="boostdep_version", default="1.73.0", type=str, help="boostdep version")
    parser.add_argument("-u", dest="git_url", default=BOOST_GIT_URL, help="boost git url")
    parser.add_argument("-U", dest="git_update", action="store_true", help="update the git repo")
    parser.add_argument("-o", dest="outputdir", default=None, type=Path, help="output dependency dir")

    version_group = parser.add_mutually_exclusive_group(required=True)
    version_group.add_argument("-v", dest="boost_version", help="boost version")
    version_group.add_argument("-A", dest="boost_version", action="store_const", const=None, help="boost version")
    ns = parser.parse_args(args)

    if not ns.tmppath:
        ns.tmppath = Path(tempfile.gettempdir())
    if not ns.outputdir:
        ns.outputdir = Path("dependencies")

    ns.outputdir.mkdir(exist_ok=True)

    git_update_done = False
    boostdep_installed = False

    if ns.boost_version is None:
        conan_data = yaml.safe_load(Path("conandata.yml").open())
        boost_versions = list(conan_data["sources"].keys())
    else:
        boost_versions = [ns.boost_version]

    for boost_version in boost_versions:
        print("Starting {}".format(boost_version))
        boost_collector = BoostDependencyBuilder(
            boost_version=boost_version,
            boostdep_version=ns.boostdep_version,
            git_url=ns.git_url,
            outputdir=ns.outputdir,
            tmppath=ns.tmppath,
        )
        if ns.git_update and not git_update_done:
            boost_collector.do_git_update()

        boost_collector.do_git_submodule_update()

        if not boostdep_installed:
            boost_collector.do_install_boostdep()
            boostdep_installed = True

        boost_collector.do_create_dependency_file()


if __name__ == "__main__":
    main()

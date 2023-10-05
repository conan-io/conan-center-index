# TODO: verify the Conan v2 migration

import os
from contextlib import nullcontext

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.android import android_abi
from conan.tools.apple import (
    XCRun,
    fix_apple_shared_install_name,
    is_apple_os,
    to_apple_arch,
)
from conan.tools.build import (
    build_jobs,
    can_run,
    check_min_cppstd,
    cross_building,
    default_cppstd,
    stdcpp_library,
    valid_min_cppstd,
)
from conan.tools.cmake import (
    CMake,
    CMakeDeps,
    CMakeToolchain,
    cmake_layout,
)
from conan.tools.env import (
    Environment,
    VirtualBuildEnv,
    VirtualRunEnv,
)
from conan.tools.files import (
    apply_conandata_patches,
    chdir,
    collect_libs,
    copy,
    download,
    export_conandata_patches,
    get,
    load,
    mkdir,
    patch,
    patches,
    rename,
    replace_in_file,
    rm,
    rmdir,
    save,
    symlinks,
    unzip,
)
from conan.tools.gnu import (
    Autotools,
    AutotoolsDeps,
    AutotoolsToolchain,
    PkgConfig,
    PkgConfigDeps,
)
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import (
    MSBuild,
    MSBuildDeps,
    MSBuildToolchain,
    NMakeDeps,
    NMakeToolchain,
    VCVars,
    check_min_vs,
    is_msvc,
    is_msvc_static_runtime,
    msvc_runtime_flag,
    unix_path,
    unix_path_package_info_legacy,
    vs_layout,
)
from conan.tools.scm import Version
from conan.tools.system import package_manager
from io import StringIO
import os
import re
import shutil


class CmakePython3Abi(object):
    def __init__(self, debug, pymalloc, unicode):
        self.debug, self.pymalloc, self.unicode = debug, pymalloc, unicode

    _cmake_lut = {
        None: "ANY",
        True: "ON",
        False: "OFF",
    }

    @property
    def suffix(self):
        return "{}{}{}".format(
            "d" if self.debug else "", "m" if self.pymalloc else "", "u" if self.unicode else ""
        )

    @property
    def cmake_arg(self):
        return ";".join(self._cmake_lut[a] for a in (self.debug, self.pymalloc, self.unicode))


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _py_version(self):
        return re.match(r"^([0-9.]+)", self.dependencies["cpython"].ref.version).group(1)

    @property
    def _pymalloc(self):
        return bool(self.dependencies["cpython"].options.get_safe("pymalloc", False))

    @property
    def _cmake_abi(self):
        if self._py_version < Version(self, "3.8"):
            return CmakePython3Abi(
                debug=self.settings.build_type == "Debug", pymalloc=self._pymalloc, unicode=False
            )
        else:
            return CmakePython3Abi(debug=self.settings.build_type == "Debug", pymalloc=False, unicode=False)

    @property
    def _cmake_try_FindPythonX(self):
        if is_msvc(self) and self.settings.build_type == "Debug":
            return False
        return True

    @property
    def _supports_modules(self):
        return not is_msvc(self) or self.dependencies["cpython"].options.shared

    def generate(self):
        tc = CMakeToolchain(self)
        py_major = Version(self.dependencies["cpython"]).major
        tc.variables["BUILD_MODULE"] = self._supports_modules
        tc.variables["PY_VERSION_MAJOR"] = py_major
        tc.variables["PY_VERSION_MAJOR_MINOR"] = ".".join(self._py_version.split(".")[:2])
        tc.variables["PY_FULL_VERSION"] = self.dependencies["cpython"].ref.version
        tc.variables["PY_VERSION"] = self._py_version
        tc.variables["PY_VERSION_SUFFIX"] = self._cmake_abi.suffix
        tc.variables["PYTHON_EXECUTABLE"] = self.conf_info.get("user.cpython:python")
        tc.variables["USE_FINDPYTHON_X".format(py_major)] = self._cmake_try_FindPythonX
        tc.variables[f"Python{py_major}_EXECUTABLE"] = self.conf_info.get("user.cpython:python")
        tc.variables[f"Python{py_major}_ROOT_DIR"] = self.dependencies["cpython"].package_folder
        tc.variables[f"Python{py_major}_USE_STATIC_LIBS"] = not self.dependencies["cpython"].options.shared
        tc.variables[f"Python{py_major}_FIND_FRAMEWORK"] = "NEVER"
        tc.variables[f"Python{py_major}_FIND_REGISTRY"] = "NEVER"
        tc.variables[f"Python{py_major}_FIND_IMPLEMENTATIONS"] = "CPython"
        tc.variables[f"Python{py_major}_FIND_STRATEGY"] = "LOCATION"

        if not is_msvc(self):
            if Version(self._py_version) < Version(self, "3.8"):
                tc.variables["Python{}_FIND_ABI".format(py_major)] = self._cmake_abi.cmake_arg

        if not cross_building(self, skip_x64_x86=True):
            if self._supports_modules:
                with vcvars(self.settings) if is_msvc(self) else nullcontext():
                    modsrcfolder = (
                        "py2" if Version(self.dependencies["cpython"].ref.version).major < "3" else "py3"
                    )
                    mkdir(self, os.path.join(self.build_folder, modsrcfolder))
                    for fn in os.listdir(os.path.join(self.source_folder, modsrcfolder)):
                        shutil.copy(
                            os.path.join(self.source_folder, modsrcfolder, fn),
                            os.path.join(self.build_folder, modsrcfolder, fn),
                        )
                    shutil.copy(
                        os.path.join(self.source_folder, "setup.py"),
                        os.path.join(self.build_folder, "setup.py"),
                    )
                    env = {
                        "DISTUTILS_USE_SDK": "1",
                        "MSSdk": "1",
                    }
                    env.update(**AutoToolsBuildEnvironment(self).vars)
                    with environment_append(self, env):
                        setup_args = [
                            "{}/setup.py".format(self.source_folder),
                            # "conan",
                            # "--install-folder", self.build_folder,
                            "build",
                            "--build-base",
                            self.build_folder,
                            "--build-platlib",
                            os.path.join(self.build_folder, "lib_setuptools"),
                        ]
                        if self.settings.build_type == "Debug":
                            setup_args.append("--debug")
                        self.run(
                            "{} {}".format(
                                self.conf_info.get("user.cpython:python"),
                                " ".join('"{}"'.format(a) for a in setup_args),
                            ),
                        )

    def build(self):
        if not cross_building(self, skip_x64_x86=True):
            python_executable = self.conf_info.get("user.cpython:python")
            command = f"{python_executable} --version"
            buffer = StringIO()
            self.run(command, stdout=buffer, ignore_errors=True)
            self.output.info(f"output: {buffer.getvalue()}")
            self.run(command)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _test_module(self, module, should_work):
        try:
            self.run(
                "{} {}/test_package.py -b {} -t {} ".format(
                    self.conf_info.get("user.cpython:python"), self.source_folder, self.build_folder, module
                ),
                run_environment=True,
            )
            works = True
        except ConanException as e:
            works = False
            exception = e
        if should_work == works:
            self.output.info("Result of test was expected.")
        else:
            if works:
                raise ConanException(f"Module '{module}' works, but should not have worked")
            else:
                self.output.warning(f"Module '{module}' does not work, but should have worked")
                raise exception

    def _cpython_option(self, name):
        try:
            return self.dependencies["cpython"].options.get_safe(name, False)
        except ConanException:
            return False

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            self.run(
                "{} -c \"print('hello world')\"".format(self.conf_info.get("user.cpython:python")),
            )

            buffer = StringIO()
            self.run(
                "{} -c \"import sys; print('.'.join(str(s) for s in sys.version_info[:3]))\"".format(
                    self.conf_info.get("user.cpython:python")
                ),
                stdout=buffer,
            )
            self.output.info(buffer.getvalue())
            version_detected = buffer.getvalue().splitlines()[-1].strip()
            if self._py_version != version_detected:
                raise ConanException(
                    "python reported wrong version. Expected {exp}. Got {res}.".format(
                        exp=self._py_version, res=version_detected
                    )
                )

            if self._supports_modules:
                self._test_module("gdbm", self._cpython_option("with_gdbm"))
                self._test_module("bz2", self._cpython_option("with_bz2"))
                self._test_module("bsddb", self._cpython_option("with_bsddb"))
                self._test_module("lzma", self._cpython_option("with_lzma"))
                self._test_module("tkinter", self._cpython_option("with_tkinter"))
                os.environ["TERM"] = "ansi"
                self._test_module("curses", self._cpython_option("with_curses"))

                self._test_module("expat", True)
                self._test_module("sqlite3", True)
                self._test_module("decimal", True)
                self._test_module("ctypes", True)

            if is_apple_os(self) and not self.dependencies["cpython"].options.shared:
                self.output.info(
                    "Not testing the module, because these seem not to work on apple when cpython is built as"
                    " a static library"
                )
                # FIXME: find out why cpython on apple does not allow to use modules linked against a static python
            else:
                if self._supports_modules:
                    with environment_append(self, {"PYTHONPATH": [os.path.join(self.build_folder, "lib")]}):
                        self.output.info("Testing module (spam) using cmake built module")
                        self._test_module("spam", True)

                    with environment_append(
                        self, {"PYTHONPATH": [os.path.join(self.build_folder, "lib_setuptools")]}
                    ):
                        self.output.info("Testing module (spam) using setup.py built module")
                        self._test_module("spam", True)

            # MSVC builds need PYTHONHOME set.
            with (
                environment_append(self, {"PYTHONHOME": self.conf_info.get("user.cpython:pythonhome")})
                if self.conf_info.get("user.cpython:module_requires_pythonhome") == "True"
                else nullcontext()
            ):
                self.run(os.path.join("bin", "test_package"), run_environment=True)

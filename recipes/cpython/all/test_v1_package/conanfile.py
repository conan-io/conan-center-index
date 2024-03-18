from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools, RunEnvironment
from conans.errors import ConanException
from conan.tools.env import VirtualRunEnv
from io import StringIO
import os
import re

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    @property
    def _py_version(self):
        return re.match(r"^([0-9.]+)", self.deps_cpp_info["cpython"].version).group(1)

    @property
    def _cmake_try_FindPythonX(self):
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            return False
        return True

    @property
    def _supports_modules(self):
        return self.settings.compiler != "Visual Studio" or self.options["cpython"].shared

    def generate(self):
        # The build also needs access to the run environment to run the python executable
        VirtualRunEnv(self).generate(scope="run")
        VirtualRunEnv(self).generate(scope="build")

    def build_requirements(self):
        # The main recipe does not require CMake, but we test with it.
        # The interesting problem that arises here is if you have CMake installed
        # with your global pip, then it will fail to run in this test package.
        # To avoid that, just add a requirement on CMake.
        self.tool_requires("cmake/[>=3.15 <4]")

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            command = "{} --version".format(self.deps_user_info["cpython"].python)
            buffer = StringIO()
            self.run(command, output=buffer, ignore_errors=True, run_environment=True)
            self.output.info("output: %s" % buffer.getvalue())
            self.run(command, run_environment=True)

        cmake = CMake(self)
        cmake.definitions["BUILD_MODULE"] = self._supports_modules
        cmake.definitions["PY_VERSION_MAJOR_MINOR"] = ".".join(self._py_version.split(".")[:2])
        cmake.definitions["PY_FULL_VERSION"] = self.deps_cpp_info["cpython"].version
        cmake.definitions["PY_VERSION"] = self._py_version
        cmake.definitions["PY_VERSION_SUFFIX"] = "d" if self.settings.build_type == "Debug" else ""
        cmake.definitions["PYTHON_EXECUTABLE"] = self.deps_user_info["cpython"].python
        cmake.definitions["USE_FINDPYTHON_X"] = self._cmake_try_FindPythonX
        cmake.definitions["Python3_EXECUTABLE"] = self.deps_user_info["cpython"].python
        cmake.definitions["Python3_ROOT_DIR"] = self.deps_cpp_info["cpython"].rootpath
        cmake.definitions["Python3_USE_STATIC_LIBS"] = not self.options["cpython"].shared
        cmake.definitions["Python3_FIND_FRAMEWORK"] = "NEVER"
        cmake.definitions["Python3_FIND_REGISTRY"] = "NEVER"
        cmake.definitions["Python3_FIND_IMPLEMENTATIONS"] = "CPython"
        cmake.definitions["Python3_FIND_STRATEGY"] = "LOCATION"

        with tools.environment_append(RunEnvironment(self).vars):
            cmake.configure()
        cmake.build()

        if not tools.cross_building(self, skip_x64_x86=True):
            if self._supports_modules:
                with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                    env = {
                        "DISTUTILS_USE_SDK": "1",
                        "MSSdk": "1"
                    }
                    env.update(**AutoToolsBuildEnvironment(self).vars)
                    with tools.environment_append(env):
                        setup_args = [
                            os.path.join(self.source_folder, "..", "test_package", "setup.py"),
                            "build",
                            "--build-base", self.build_folder,
                            "--build-platlib", os.path.join(self.build_folder, "lib_setuptools"),
                            # Bandaid fix: setuptools places temporary files in a subdirectory of the build folder where the
                            # entirety of the absolute path up to this folder is appended (with seemingly no way to stop this),
                            # essentially doubling the path length. This may run into Windows max path lengths, so we give ourselves
                            # a little bit of wiggle room by making this directory name as short as possible. One of the directory
                            # names goes from (for example) "temp.win-amd64-3.10-pydebug" to "t", saving us roughly 25 characters.
                            "--build-temp", "t",
                        ]
                        if self.settings.build_type == "Debug":
                            setup_args.append("--debug")
                        self.run("{} {}".format(self.deps_user_info["cpython"].python, " ".join("\"{}\"".format(a) for a in setup_args)), run_environment=True)

    def _test_module(self, module, should_work):
        try:
            self.run("{} {}/../test_package/test_package.py -b {} -t {} ".format(
                self.deps_user_info["cpython"].python, self.source_folder, self.build_folder, module), run_environment=True)
            works = True
        except ConanException as e:
            works = False
            exception = e
        if should_work == works:
            self.output.info("Result of test was expected.")
        else:
            if works:
                raise ConanException("Module '{}' works, but should not have worked".format(module))
            else:
                self.output.warn("Module '{}' does not work, but should have worked".format(module))
                raise exception

    def _cpython_option(self, name):
        try:
            return getattr(self.options["cpython"], name, False)
        except ConanException:
            return False

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("{} -c \"print('hello world')\"".format(self.deps_user_info["cpython"].python), run_environment=True)

            buffer = StringIO()
            self.run("{} -c \"import sys; print('.'.join(str(s) for s in sys.version_info[:3]))\"".format(self.deps_user_info["cpython"].python), run_environment=True, output=buffer)
            self.output.info(buffer.getvalue())
            version_detected = buffer.getvalue().splitlines()[-1].strip()
            if self._py_version != version_detected:
                raise ConanException("python reported wrong version. Expected {exp}. Got {res}.".format(exp=self._py_version, res=version_detected))

            if self._supports_modules:
                self._test_module("gdbm", self._cpython_option("with_gdbm"))
                self._test_module("bz2", self._cpython_option("with_bz2"))
                self._test_module("lzma", self._cpython_option("with_lzma"))
                self._test_module("tkinter", self._cpython_option("with_tkinter"))
                with tools.environment_append({"TERM": "ansi"}):
                    self._test_module("curses", self._cpython_option("with_curses"))

                self._test_module("expat", True)
                self._test_module("sqlite3", True)
                self._test_module("decimal", True)
                self._test_module("ctypes", True)

            if tools.is_apple_os(self.settings.os) and not self.options["cpython"].shared:
                self.output.info("Not testing the module, because these seem not to work on apple when cpython is built as a static library")
                # FIXME: find out why cpython on apple does not allow to use modules linked against a static python
            else:
                if self._supports_modules:
                    with tools.environment_append({"PYTHONPATH": [os.path.join(self.build_folder, "lib")]}):
                        self.output.info("Testing module (spam) using cmake built module")
                        self._test_module("spam", True)

                    with tools.environment_append({"PYTHONPATH": [os.path.join(self.build_folder, "lib_setuptools")]}):
                        self.output.info("Testing module (spam) using setup.py built module")
                        self._test_module("spam", True)

            # MSVC builds need PYTHONHOME set. Linux and Mac don't require it to be set if tested after building,
            # but if the package is relocated then it needs to be set.
            with tools.environment_append({"PYTHONHOME": self.deps_user_info["cpython"].pythonhome}):
                self.run(os.path.join("bin", "test_package"), run_environment=True)

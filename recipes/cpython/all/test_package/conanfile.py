from conans import ConanFile, CMake, tools, RunEnvironment
from conans.errors import ConanException
from io import StringIO
import os
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
            "d" if self.debug else "",
            "m" if self.pymalloc else "",
            "u" if self.unicode else "",
        )

    @property
    def cmake_arg(self):
        return ";".join(self._cmake_lut[a] for a in (self.debug, self.pymalloc, self.unicode))


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    @property
    def _py_version(self):
        return self.deps_cpp_info["cpython"].version

    @property
    def _cmake_abi(self):
        if self._py_version < tools.Version("3.8"):
            return CmakePython3Abi(
                debug=self.settings.build_type == "Debug",
                pymalloc=bool(self.options["cpython"].pymalloc),
                unicode=False,
            )
        else:
            return CmakePython3Abi(
                debug=self.settings.build_type == "Debug",
                pymalloc=False,
                unicode=False,
            )

    def build(self):
        cmake = CMake(self)
        py_major = self.deps_cpp_info["cpython"].version.split(".")[0]
        cmake.definitions["PY_VERSION_MAJOR"] = py_major
        cmake.definitions["PY_VERSION_MAJOR_MINOR"] = ".".join(self._py_version.split(".")[:2])
        cmake.definitions["PY_VERSION"] = self._py_version
        cmake.definitions["PY_VERSION_SUFFIX"] = self._cmake_abi.suffix
        cmake.definitions["PYTHON_EXECUTABLE"] = tools.get_env("PYTHON")
        cmake.definitions["Python{}_ROOT_DIR".format(py_major)] = self.deps_cpp_info["cpython"].rootpath
        cmake.definitions["Python{}_USE_STATIC_LIBS".format(py_major)] = not self.options["cpython"].shared
        cmake.definitions["Python{}_FIND_REGISTRY".format(py_major)] = "NEVER"
        cmake.definitions["Python{}_FIND_IMPLEMENTATIONS".format(py_major)] = "CPython"
        cmake.definitions["Python{}_FIND_STRATEGY".format(py_major)] = "LOCATION"

        if self.settings.compiler != "Visual Studio":
            if tools.Version(self._py_version) < tools.Version("3.8"):
                cmake.definitions["Python{}_FIND_ABI".format(py_major)] = self._cmake_abi.cmake_arg

        with tools.environment_append(RunEnvironment(self).vars):
            cmake.configure()
        cmake.build()

        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            modsrcfolder = "py2" if tools.Version(self.deps_cpp_info["cpython"].version).major < "3" else "py3"
            shutil.copytree(os.path.join(self.source_folder, modsrcfolder), os.path.join(self.build_folder, modsrcfolder))
            shutil.copy(os.path.join(self.source_folder, "setup.py"), os.path.join(self.build_folder, "setup.py"))
            with tools.environment_append({"DISTUTILS_USE_SDK": "1", "MSSdk": "1"}):
                setup_args = [
                    "{}/setup.py".format(self.source_folder),
                    "conan",
                    "--install-folder", self.build_folder,
                    "build",
                    "--build-base", self.build_folder,
                    "--build-platlib", os.path.join(self.build_folder, "lib_setuptools"),
                ]
                if self.settings.build_type == "Debug":
                    setup_args.append("--debug")
                self.run("{} {}".format(tools.get_env("PYTHON"), " ".join("\"{}\"".format(a) for a in setup_args)), run_environment=True)

    def _test_module(self, module):
        self.run("{} {}/test_package.py -b {} -t {} ".format(tools.get_env("PYTHON"), self.source_folder, self.build_folder, module), run_environment=True)

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run("{} -c \"print('hello world')\"".format(tools.get_env("PYTHON")), run_environment=True)

            buffer = StringIO()
            self.run("{} -c \"import sys; print('.'.join(str(s) for s in sys.version_info[:3]))\"".format(tools.get_env("PYTHON")), run_environment=True, output=buffer)
            version_detected = buffer.getvalue().splitlines()[-1].strip()
            if version_detected != self.deps_cpp_info["cpython"].version:
                raise ConanException("python reported wrong version. Expected {exp}. Got {res}.".format(exp=self._py_version, res=version_detected))

            if self.options["cpython"].with_gdbm:
                self._test_module("gdbm")
            if self.options["cpython"].with_bz2:
                self._test_module("bz2")
            if self.options["cpython"].with_bsddb:
                self._test_module("bsddb")
            if self.options["cpython"].with_lzma:
                self._test_module("lzma")

            self._test_module("expat")
            self._test_module("sqlite3")
            self._test_module("decimal")

            # with tools.environment_append({"PYTHONPATH": [os.path.join(self.build_folder, "lib")]}):
            #     self.output.info("Testing module (spam) using cmake built module")
            #     self._test_module("spam")

            with tools.environment_append({"PYTHONPATH": [os.path.join(self.build_folder, "lib_setuptools")]}):
                self.output.info("Testing module (spam) using setup.py built module")
                self._test_module("spam")

            self.run(os.path.join("bin", "test_package"), run_environment=True)

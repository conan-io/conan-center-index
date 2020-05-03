from conans import ConanFile, CMake, tools
from conans.errors import ConanException
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["PYTHON_EXECUTABLE"] = tools.get_env("PYTHON")
        cmake.definitions["Python_ADDITIONAL_VERSIONS"] = ";".join([".".join(self.deps_cpp_info["cpython"].version.split(".")[:2]), self.deps_cpp_info["cpython"].version.split(".")[0]])
        cmake.definitions["PYTHON_EXACT_VERSION"] = self.deps_cpp_info["cpython"].version
        # cmake.definitions["Python2_EXECUTABLE"] = tools.get_env("PYTHON")
        cmake.definitions["Python2_ROOT_DIR"] = self.deps_cpp_info["cpython"].rootpath
        cmake.definitions["Python2_USE_STATIC_LIBS"] = not self.options["cpython"].shared
        cmake.definitions["Python2_FIND_REGISTRY"] = "NEVER"
        cmake.definitions["Python2_FIND_IMPLEMENTATIONS"] = "CPython"
        cmake.definitions["Python2_FIND_STRATEGY"] = "LOCATION"
        from conans import RunEnvironment
        with tools.environment_append(RunEnvironment(self).vars):
            cmake.configure()
            # cmake.configure(args=["--trace", "--trace-expand"])
        cmake.build()

    def _test_module(self, module):
        self.run("{} {}/test_package.py -b {} -t {}".format(tools.get_env("PYTHON"), self.source_folder, self.build_folder, module), run_environment=True)

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run("{} -c \"print 'hello world'\"".format(tools.get_env("PYTHON")), run_environment=True)

            buffer = StringIO()
            self.run("{} -c \"import sys; print('.'.join(str(s) for s in sys.version_info[:3]))\"".format(tools.get_env("PYTHON")), run_environment=True, output=buffer)
            version_detected = buffer.getvalue().splitlines()[-1].strip()
            if version_detected != self.deps_cpp_info["cpython"].version:
                raise ConanException("python reported wrong version. Expected {exp}. Got {res}.".format(exp=self.deps_cpp_info["cpython"].version, res=version_detected))

            if self.options["cpython"].with_gdbm:
                self._test_module("gdbm")
            if self.options["cpython"].with_bz2:
                self._test_module("bz2")
            if self.options["cpython"].with_bsddb:
                self._test_module("bsddb")

            self._test_module("expat")

            with tools.environment_append({"PYTHONPATH": [os.path.join(self.build_folder, "lib")]}):
                self._test_module("spam")

            self.run(os.path.join("bin", "test_package"), run_environment=True)

from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package"

    def _boost_option(self, name, default):
        try:
            return getattr(self.options["boost"], name, default)
        except (AttributeError, ConanException):
            return default

    def build(self):
        # FIXME: tools.vcvars added for clang-cl. Remove once conan supports clang-cl properly. (https://github.com/conan-io/conan-center-index/pull/1453)
        with tools.vcvars(self.settings) if (self.settings.os == "Windows" and self.settings.compiler == "clang") else tools.no_op():
            cmake = CMake(self)
            cmake.definitions["HEADER_ONLY"] = self.options["boost"].header_only
            if not self.options["boost"].header_only:
                cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
            cmake.definitions["WITH_PYTHON"] = not self.options["boost"].without_python
            if not self.options["boost"].without_python:
                pyversion = tools.Version(self.options["boost"].python_version)
                cmake.definitions["Python_ADDITIONAL_VERSIONS"] = "{}.{}".format(pyversion.major, pyversion.minor)
                cmake.definitions["PYTHON_COMPONENT_SUFFIX"] = "{}{}".format(pyversion.major, pyversion.minor)
            cmake.definitions["WITH_RANDOM"] = not self.options["boost"].without_random
            cmake.definitions["WITH_REGEX"] = not self.options["boost"].without_regex
            cmake.definitions["WITH_TEST"] = not self.options["boost"].without_test
            cmake.definitions["WITH_COROUTINE"] = not self.options["boost"].without_coroutine
            cmake.definitions["WITH_CHRONO"] = not self.options["boost"].without_chrono
            cmake.definitions["WITH_FIBER"] = not self.options["boost"].without_fiber
            cmake.definitions["WITH_LOCALE"] = not self.options["boost"].without_locale
            cmake.definitions["WITH_NOWIDE"] = not self._boost_option("without_nowide", True)
            cmake.definitions["WITH_JSON"] = not self._boost_option("without_json", True)
            cmake.configure()
            cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return
        self.run(os.path.join("bin", "lambda_exe"), run_environment=True)
        if self.options["boost"].header_only:
            return
        if not self.options["boost"].without_random:
            self.run(os.path.join("bin", "random_exe"), run_environment=True)
        if not self.options["boost"].without_regex:
            self.run(os.path.join("bin", "regex_exe"), run_environment=True)
        if not self.options["boost"].without_test:
            self.run(os.path.join("bin", "test_exe"), run_environment=True)
        if not self.options["boost"].without_coroutine:
            self.run(os.path.join("bin", "coroutine_exe"), run_environment=True)
        if not self.options["boost"].without_chrono:
            self.run(os.path.join("bin", "chrono_exe"), run_environment=True)
        if not self.options["boost"].without_fiber:
            self.run(os.path.join("bin", "fiber_exe"), run_environment=True)
        if not self.options["boost"].without_locale:
            self.run(os.path.join("bin", "locale_exe"), run_environment=True)
        if not self._boost_option("without_nowide", True):
            self.run("{} {}".format(os.path.join("bin", "nowide_exe"), os.path.join(self.source_folder, "conanfile.py")), run_environment=True)
        if not self._boost_option("without_json", True):
            self.run(os.path.join("bin", "json_exe"), run_environment=True)
        if not self.options["boost"].without_python:
            with tools.environment_append({"PYTHONPATH": "{}:{}".format("bin", "lib")}):
                self.run("{} {}".format(self.options["boost"].python_executable, os.path.join(self.source_folder, "python.py")), run_environment=True)
            self.run(os.path.join("bin", "numpy_exe"), run_environment=True)

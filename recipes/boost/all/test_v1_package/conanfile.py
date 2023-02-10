from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
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
                cmake.definitions["PYTHON_VERSION_TO_SEARCH"] = pyversion
                cmake.definitions["Python_EXECUTABLE"] = self.options["boost"].python_executable
            cmake.definitions["WITH_RANDOM"] = not self.options["boost"].without_random
            cmake.definitions["WITH_REGEX"] = not self.options["boost"].without_regex
            cmake.definitions["WITH_TEST"] = not self.options["boost"].without_test
            cmake.definitions["WITH_COROUTINE"] = not self.options["boost"].without_coroutine
            cmake.definitions["WITH_CHRONO"] = not self.options["boost"].without_chrono
            cmake.definitions["WITH_FIBER"] = not self.options["boost"].without_fiber
            cmake.definitions["WITH_LOCALE"] = not self.options["boost"].without_locale
            cmake.definitions["WITH_NOWIDE"] = not self._boost_option("without_nowide", True)
            cmake.definitions["WITH_JSON"] = not self._boost_option("without_json", True)
            cmake.definitions["WITH_STACKTRACE"] = not self.options["boost"].without_stacktrace
            cmake.definitions["WITH_STACKTRACE_ADDR2LINE"] = self.deps_user_info["boost"].stacktrace_addr2line_available
            cmake.definitions["WITH_STACKTRACE_BACKTRACE"] = self._boost_option("with_stacktrace_backtrace", False)
            cmake.definitions["WITH_URL"] = not self._boost_option("without_url", True)
            if self.options["boost"].namespace != 'boost' and not self.options["boost"].namespace_alias:
                cmake.definitions['BOOST_NAMESPACE'] = self.options["boost"].namespace
            cmake.configure()
            # Disable parallel builds because c3i (=conan-center's test/build infrastructure) seems to choke here
            cmake.parallel = False
            cmake.build()

    def test(self):
        if tools.cross_building(self):
            return
        self.run(f"ctest --output-on-failure -C {self.settings.build_type}", run_environment=True)
    

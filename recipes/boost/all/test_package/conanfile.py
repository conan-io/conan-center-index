import os
from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    def _boost_option(self, name, default):
        try:
            return getattr(self.dependencies["boost"].options, name, default)
        except (AttributeError, ConanException):
            return default

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["HEADER_ONLY"] = self.dependencies["boost"].options.header_only
        if not self.dependencies["boost"].options.header_only:
            tc.cache_variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.shared
        tc.cache_variables["WITH_PYTHON"] = not self.dependencies["boost"].options.without_python
        if not self.dependencies["boost"].options.without_python:
            pyversion = self.dependencies["boost"].options.python_version
            tc.cache_variables["PYTHON_VERSION_TO_SEARCH"] = pyversion
            tc.cache_variables["Python_EXECUTABLE"] = self.dependencies["boost"].options.python_executable
        tc.cache_variables["WITH_RANDOM"] = not self.dependencies["boost"].options.without_random
        tc.cache_variables["WITH_REGEX"] = not self.dependencies["boost"].options.without_regex
        tc.cache_variables["WITH_TEST"] = not self.dependencies["boost"].options.without_test
        tc.cache_variables["WITH_COROUTINE"] = not self.dependencies["boost"].options.without_coroutine
        tc.cache_variables["WITH_CHRONO"] = not self.dependencies["boost"].options.without_chrono
        tc.cache_variables["WITH_FIBER"] = not self.dependencies["boost"].options.without_fiber
        tc.cache_variables["WITH_LOCALE"] = not self.dependencies["boost"].options.without_locale
        tc.cache_variables["WITH_NOWIDE"] = not self._boost_option("without_nowide", True)
        tc.cache_variables["WITH_JSON"] = not self._boost_option("without_json", True)
        tc.cache_variables["WITH_PROCESS"] = not self._boost_option("without_process", True)
        tc.cache_variables["WITH_STACKTRACE"] = not self.dependencies["boost"].options.without_stacktrace
        tc.cache_variables["WITH_URL"] = not self._boost_option("without_url", True)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return

        for file in os.listdir(self.cpp.build.bindirs[0]):
            if file.startswith("test_boost_"):
                if self.settings.os == "Windows" and not file.endswith(".exe"):
                    continue
                bin_path = os.path.join(self.cpp.build.bindirs[0], file)
                self.run(bin_path, env="conanrun")

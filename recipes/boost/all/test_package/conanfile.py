from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def _boost_option(self, name, default):
        try:
            return getattr(self.options["boost"], name, default)
        except (AttributeError, ConanException):
            return default

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HEADER_ONLY"] = self.dependencies["boost"].options.header_only
        if not self.dependencies["boost"].options.header_only:
            tc.variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.shared
        tc.variables["WITH_PYTHON"] = not self.dependencies["boost"].options.without_python
        if not self.dependencies["boost"].options.without_python:
            pyversion = Version(self.dependencies["boost"].options.python_version)
            tc.variables["Python_ADDITIONAL_VERSIONS"] = f"{pyversion.major}.{pyversion.minor}"
            tc.variables["PYTHON_COMPONENT_SUFFIX"] = f"{pyversion.major}.{pyversion.minor}"
        tc.variables["WITH_RANDOM"] = not self.dependencies["boost"].options.without_random
        tc.variables["WITH_REGEX"] = not self.dependencies["boost"].options.without_regex
        tc.variables["WITH_TEST"] = not self.dependencies["boost"].options.without_test
        tc.variables["WITH_COROUTINE"] = not self.dependencies["boost"].options.without_coroutine
        tc.variables["WITH_CHRONO"] = not self.dependencies["boost"].options.without_chrono
        tc.variables["WITH_FIBER"] = not self.dependencies["boost"].options.without_fiber
        tc.variables["WITH_LOCALE"] = not self.dependencies["boost"].options.without_locale
        tc.variables["WITH_NOWIDE"] = not self._boost_option("without_nowide", True)
        tc.variables["WITH_JSON"] = not self._boost_option("without_json", True)
        tc.variables["WITH_STACKTRACE"] = not self.dependencies["boost"].options.without_stacktrace
        tc.variables["WITH_STACKTRACE_ADDR2LINE"] = self.deps_user_info["boost"].stacktrace_addr2line_available
        tc.variables["WITH_STACKTRACE_BACKTRACE"] = self._boost_option("with_stacktrace_backtrace", False)
        if self.dependencies["boost"].options.namespace != 'boost' and not self.dependencies["boost"].options.namespace_alias:
            tc.variables['BOOST_NAMESPACE'] = self.dependencies["boost"].options.namespace
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        bindir = self.cpp.build.bindirs[0]
        self.run(os.path.join(bindir, "lambda_exe"), env="conanrun")
        if self.options["boost"].header_only:
            return
        if not self.options["boost"].without_random:
            self.run(os.path.join(bindir, "random_exe"), env="conanrun")
        if not self.options["boost"].without_regex:
            self.run(os.path.join(bindir, "regex_exe"), env="conanrun")
        if not self.options["boost"].without_test:
            self.run(os.path.join(bindir, "test_exe"), env="conanrun")
        if not self.options["boost"].without_coroutine:
            self.run(os.path.join(bindir, "coroutine_exe"), env="conanrun")
        if not self.options["boost"].without_chrono:
            self.run(os.path.join(bindir, "chrono_exe"), env="conanrun")
        if not self.options["boost"].without_fiber:
            self.run(os.path.join(bindir, "fiber_exe"), env="conanrun")
        if not self.options["boost"].without_locale:
            self.run(os.path.join(bindir, "locale_exe"), env="conanrun")
        if not self._boost_option("without_nowide", True):
            bin_nowide = os.path.join(bindir, "nowide_exe")
            conanfile = os.path.join(self.source_folder, "conanfile.py")
            self.run(f"{bin_nowide} {conanfile}", env="conanrun")
        if not self._boost_option("without_json", True):
            self.run(os.path.join(bindir, "json_exe"), env="conanrun")
        if not self.options["boost"].without_python:
            with tools_legacy.environment_append({"PYTHONPATH": "bin:lib"}):
                python_executable = self.options["boost"].python_executable
                python_script = os.path.join(self.source_folder, "python.py")
                self.run(f"{python_executable} {python_script}", env="conanrun")
            self.run(os.path.join(bindir, "numpy_exe"), env="conanrun")
        if not self.options["boost"].without_stacktrace:
            self.run(os.path.join(bindir, "stacktrace_noop_exe"), env="conanrun")
            if str(self.deps_user_info["boost"].stacktrace_addr2line_available) == "True":
                self.run(os.path.join(bindir, "stacktrace_addr2line_exe"), env="conanrun")
            if self.settings.os == "Windows":
                self.run(os.path.join(bindir, "stacktrace_windbg_exe"), env="conanrun")
                self.run(os.path.join(bindir, "stacktrace_windbg_cached_exe"), env="conanrun")
            else:
                self.run(os.path.join(bindir, "stacktrace_basic_exe"), env="conanrun")
            if self._boost_option("with_stacktrace_backtrace", False):
                self.run(os.path.join(bindir, "stacktrace_backtrace_exe"), env="conanrun")

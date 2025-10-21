from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

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
        tc.cache_variables["WITH_PYTHON"] = False
        tc.cache_variables["WITH_RANDOM"] = True
        tc.cache_variables["WITH_REGEX"] = True
        tc.cache_variables["WITH_TEST"] = True
        tc.cache_variables["WITH_COROUTINE"] = True
        tc.cache_variables["WITH_CHRONO"] = True
        tc.cache_variables["WITH_FIBER"] = True
        tc.cache_variables["WITH_LOCALE"] = True
        tc.cache_variables["WITH_NOWIDE"] = True
        tc.cache_variables["WITH_JSON"] = True
        tc.cache_variables["WITH_PROCESS"] = True
        tc.cache_variables["WITH_STACKTRACE"] = True
        tc.cache_variables["WITH_STACKTRACE_ADDR2LINE"] = True
        tc.cache_variables["WITH_STACKTRACE_BACKTRACE"] = False # needs a patch
        tc.cache_variables["WITH_URL"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        with chdir(self, self.folders.build_folder):
            # When boost and its dependencies are built as shared libraries,
            # the test executables need to locate them. Typically the
            # `conanrun` env should be enough, but this may cause problems on macOS
            # where the CMake installation has dependencies on Apple-provided
            # system libraries that are incompatible with Conan-provided ones.
            # When `conanrun` is enabled, DYLD_LIBRARY_PATH will also apply
            # to ctest itself. Given that CMake already embeds RPATHs by default,
            # we can bypass this by using the `conanbuild` environment on
            # non-Windows platforms, while still retaining the correct behaviour.
            env = "conanrun" if self.settings.os == "Windows" else "conanbuild"
            self.run(f"ctest --output-on-failure -C {self.settings.build_type}", env=env)

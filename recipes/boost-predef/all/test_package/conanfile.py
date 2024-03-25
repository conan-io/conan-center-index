from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
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

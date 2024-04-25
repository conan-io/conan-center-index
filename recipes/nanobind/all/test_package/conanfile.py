from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("cpython/3.12.2", run=True)

    def build_requirements(self):
        # Required for find_package(Python)
        self.tool_requires("cpython/<host_version>")
        # Required for Development.Module in find_package(Python)
        self.tool_requires("cmake/[>=3.18 <4]")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run('python -c "import test_package; print(test_package.add(2, 3))"',
                     env="conanrun", cwd=self.cpp.build.bindir)

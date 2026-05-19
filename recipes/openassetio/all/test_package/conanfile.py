from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("cpython/3.12.7")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27 <5]")
        self.tool_requires("cpython/<host_version>")

    def generate(self):
        tc = CMakeDeps(self)
        tc.generate()
        tc = CMakeToolchain(self)

        tc.variables["OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI"] = self.settings.get_safe("compiler.libcxx") == "libstdc++11"
        tc.variables["OPENASSETIOTEST_ENABLE_PYTHON"] = self.dependencies["openassetio"].options.with_python

        if self.dependencies["openassetio"].options.with_python:
            if self.settings.compiler == "clang":
                # Work around cpython recipe bug.
                # FIXME: remove once fixed upstream.
                tc.variables["CMAKE_EXE_LINKER_FLAGS"] = "-lpthread"

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            cmake = CMake(self)
            cmake.test()

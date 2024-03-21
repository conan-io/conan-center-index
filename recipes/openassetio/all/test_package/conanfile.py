import pathlib

from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")
        self.tool_requires("cpython/3.10.0")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI"] = self.settings.get_safe("compiler.libcxx") == "libstdc++11"
        tc.variables["OPENASSETIOTEST_ENABLE_PYTHON"] = self.dependencies["openassetio"].options.with_python

        if self.dependencies["openassetio"].options.with_python:
            if is_msvc(self):
                tc.variables["Python_LIBRARY"] = self._python_windows_lib
            if self.settings.compiler == "clang":
                # Work around cpython recipe bug.
                # FIXME: remove once fixed upstream.
                tc.variables["CMAKE_EXE_LINKER_FLAGS"] = "-lpthread"

        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            cmake = CMake(self)
            cmake.test()

    @property
    def _python_windows_lib(self):
        pth = pathlib.Path(
            self.dependencies.build["cpython"].package_folder,
            self.dependencies.build["cpython"].cpp_info.components["embed"].libdir,
            self.dependencies.build["cpython"].cpp_info.components["embed"].libs[0])
        pth = pth.with_suffix(".lib")
        return pth.as_posix()

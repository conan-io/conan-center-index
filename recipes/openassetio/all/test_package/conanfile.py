import pathlib

from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires("cmake/3.25.3")

    def requirements(self):
        self.requires(self.tested_reference_str)

        if "with_python" not in self.options["openassetio"] or self.options["openassetio"].with_python:
            self.requires("cpython/3.9.7")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI"] = self.settings.get_safe("compiler.libcxx") == "libstdc++11"
        tc.variables["OPENASSETIOTEST_ENABLE_PYTHON"] = self.dependencies["openassetio"].options.with_python

        if self.dependencies["openassetio"].options.with_python:
            tc.variables["Python_EXECUTABLE"] = self._python_exe
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
    def _python_exe(self):
        return pathlib.Path(self.deps_user_info["cpython"].python).as_posix()

    @property
    def _python_windows_lib(self):
        pth = pathlib.Path(
            self.dependencies["cpython"].package_folder,
            self.dependencies["cpython"].cpp_info.components["embed"].libdirs[0],
            self.dependencies["cpython"].cpp_info.components["embed"].libs[0])
        pth = pth.with_suffix(".lib")
        return pth.as_posix()

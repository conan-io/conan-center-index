from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

        if "without_python" in self.options["openassetio"] and self.options["openassetio"].without_python:
            python_version = None
        elif "python_version" in self.options["openassetio"]:
            python_version = self.options['openassetio'].python_version
        else:
            python_version = "3.9.7"

        if python_version is not None:
            self.requires(f"cpython/{python_version}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        get(self, **self.conan_data["sources"][self.dependencies["openassetio"].ref.version], destination=self.source_folder, strip_root=True)
        tc = CMakeToolchain(self)

        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx is not None:
            if libcxx == "libstdc++11":
                tc.variables["OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI"] = True
            else:
                tc.variables["OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI"] = False

        if self.dependencies["openassetio"].options.without_python:
            tc.variables["OPENASSETIOTEST_ENABLE_PYTHON"] = False
        else:
            tc.variables["OPENASSETIOTEST_ENABLE_PYTHON"] = True
            tc.variables["Python_EXECUTABLE"] = self._python_exe
            if self.settings.os == "Windows":
                tc.variables["Python_LIBRARY"] = self._python_lib

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
        return self.deps_user_info["cpython"].python

    @property
    def _python_lib(self):
        return os.path.join(
            self.dependencies["cpython"].cpp_info.rootpath,
            self.dependencies["cpython"].cpp_info.components["embed"].libdirs[0],
            self.dependencies["cpython"].cpp_info.components["embed"].libs[0])

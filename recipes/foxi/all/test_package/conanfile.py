from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def config_options(self):
        # we need a shared onnxifi for testing library loading
        self.options["onnx"].shared = True

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("onnx/1.11.0")

    def layout(self):
        cmake_layout(self)

    def _get_libonnxifi_path(self):
        # deduce onnxifi library path for loading
        onnx_dep = self.dependencies["onnx"]
        libonnxifi_prefix = "" if self.settings.os == "Windows" else "lib"
        if self.settings.os == "Windows":
            libonnxifi_postfix = ".dll"
        elif self.settings.os == "Macos":
            libonnxifi_postfix = ".dylib"
        else:
            libonnxifi_postfix = ".so"
        libonnxifi_name = libonnxifi_prefix + "onnxifi" + libonnxifi_postfix
        libonnxifi_path = os.path.join(onnx_dep.package_folder, onnx_dep.cpp_info.components["onnxifi"].libdirs[0], libonnxifi_name)
        return libonnxifi_path

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ONNXIFI_PATH"] = self._get_libonnxifi_path()
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.preprocessor_definitions["ONNXIFI_REQUIRES_PTHREAD_SYMBOLS"] = "1"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

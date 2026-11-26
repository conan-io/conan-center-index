from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class MeasFlowConan(ConanFile):
    name = "measflow"
    description = "Open, high-performance binary measurement data format"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://vreitenbach.github.io/MeasFlow/"
    topics = ("measurement", "binary-format", "streaming", "automotive", "data-acquisition")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_lz4": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lz4": True,
        "with_zstd": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_lz4:
            self.requires("lz4/1.10.0")
        if self.options.with_zstd:
            self.requires("zstd/1.5.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MEAS_BUILD_TESTS"] = False
        tc.variables["MEAS_BUILD_BENCHMARKS"] = False
        tc.variables["MEAS_BUILD_QUICKSTART"] = False
        tc.variables["MEAS_WITH_LZ4"] = bool(self.options.with_lz4)
        tc.variables["MEAS_WITH_ZSTD"] = bool(self.options.with_zstd)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "c"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "measflow")
        self.cpp_info.set_property("cmake_target_name", "measflow::measflow")
        self.cpp_info.libs = ["measflow"]
        if self.options.with_lz4:
            self.cpp_info.defines.append("MEAS_HAVE_LZ4")
            self.cpp_info.requires.append("lz4::lz4")
        if self.options.with_zstd:
            self.cpp_info.defines.append("MEAS_HAVE_ZSTD")
            self.cpp_info.requires.append("zstd::zstd")
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("MEASFLOW_SHARED")

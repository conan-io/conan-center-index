from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, rmdir, copy
import os


class CLBlastConan(ConanFile):
    name = "clblast"
    description = "CLBlast is a lightweight, performant and tunable OpenCL BLAS library written in C++11."
    license = "Apache-2.0"
    topics = ("gpu", "opencl", "matrix-multiplication", "blas", "gemm", "blas-libraries", "clblas")
    homepage = "https://github.com/CNugteren/CLBlast"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.settings.os != "Macos":
            self.requires("opencl-headers/2025.07.22", transitive_headers=True)
            self.requires("opencl-icd-loader/2025.07.22")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OVERRIDE_MSVC_FLAGS_TO_MT"] = False
        tc.cache_variables["TUNERS"] = False
        tc.cache_variables["TESTS"] = False
        tc.cache_variables["SAMPLES"] = False
        tc.generate()
        deps = CMakeDeps(self)
        if self.settings.os != "Macos":
            deps.set_property("opencl-icd-loader","cmake_file_name", "OpenCL")
            deps.set_property("opencl-icd-loader", "cmake_additional_variables_prefixes", ["OPENCL"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["clblast"]
        self.cpp_info.set_property("cmake_target_name", "clblast")
        self.cpp_info.set_property("cmake_file_name", "CLBlast")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("OpenCL")

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
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
    default_options = {"shared": True, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("opencl-headers/2025.07.22")        # C headers (CL/opencl.h)
        if self.settings.os != "Macos":
            self.requires("opencl-icd-loader/2025.07.22", options={"shared": True})

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TUNERS"] = "OFF"
        tc.variables["TESTS"] = "OFF"
        tc.variables["SAMPLES"] = "OFF"
        opencl_headers = self.dependencies["opencl-headers"]
        tc.variables["OpenCL_INCLUDE_DIR"] = opencl_headers.cpp_info.aggregated_components().includedirs[0].replace("\\", "/")
        if self.settings.os != "Macos":
            opencl_icd = self.dependencies["opencl-icd-loader"]
            libdir = opencl_icd.cpp_info.aggregated_components().libdirs[0].replace("\\", "/")
            lib_name = "OpenCL.lib" if self.settings.os == "Windows" else "libOpenCL.so"
            tc.variables["OpenCL_LIBRARY"] = os.path.join(libdir, lib_name).replace("\\", "/")
        tc.generate()

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
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("OpenCL")

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.47.0"


class IttApiConan(ConanFile):
    name = "ittapi"
    license = "dual licensed under GPLv2 and 3-Clause BSD licenses"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/ittapi"
    description = (
        "The Instrumentation and Tracing Technology (ITT) API enables your application"
        " to generate and control the collection of trace data during its execution"
        " across different Intel tools."
    )
    topics = ("itt", "ittapi", "vtune", "profiler", "profiling")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],  # @note fPIC is always enabled by the underlying CMake file. So we ignore this option.
        "ptmark": [True, False],
    }
    default_options = {
        "fPIC": True,
        "ptmark": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # We have no C++ files.
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["ITT_API_IPT_SUPPORT"] = 1 if self.options.ptmark else 0
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "libittnotify.lib", src=f"bin/{self.settings.build_type}", dst=os.path.join(self.package_folder, "lib"))
        else:
            copy(self, "libittnotify.a", src=f"bin", dst=os.path.join(self.package_folder, "lib"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "BSD-3-Clause.txt", src=os.path.join(self.source_folder, "LICENSES"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "GPL-2.0-only.txt", src=os.path.join(self.source_folder, "LICENSES"), dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['libittnotify']
        else:
            self.cpp_info.libs = ['ittnotify']
            self.cpp_info.system_libs = ['dl']

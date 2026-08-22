from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0"


class IttApiConan(ConanFile):
    name = "ittapi"
    license = ("BSD-3-Clause", "GPL-2.0-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/ittapi"
    description = (
        "The Instrumentation and Tracing Technology (ITT) API enables your application"
        " to generate and control the collection of trace data during its execution"
        " across different Intel tools."
    )
    topics = ("itt", "ittapi", "vtune", "profiler", "profiling")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
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
        self.settings.compiler.rm_safe("libcxx")
        self.settings.compiler.rm_safe("cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["ITT_API_IPT_SUPPORT"] = self.options.ptmark
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.txt", src=os.path.join(self.source_folder, "LICENSES"), dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # https://github.com/intel/ittapi/blob/03f7260c96d4b437d12dceee7955ebb1e30e85ad/CMakeLists.txt#L176
        self.cpp_info.set_property("cmake_target_name", "ittapi::ittnotify")
        self.cpp_info.set_property("cmake_target_aliases", ["ittapi::ittapi"]) # for compatibility with earlier revisions of the recipe
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['libittnotify']
        else:
            self.cpp_info.libs = ['ittnotify']
            self.cpp_info.system_libs = ['dl']

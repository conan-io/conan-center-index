from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, download
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.4"


class PerfettoConan(ConanFile):
    name = "perfetto"
    description = "Performance instrumentation and tracing for Android, Linux and Chrome"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://perfetto.dev"
    topics = ("linux", "profiling", "tracing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_logging": [True, False], # switches PERFETTO_DISABLE_LOG
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_logging": False,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        download(self, filename="LICENSE", **self.conan_data["licenses"][self.version])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PERFETTO_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["PERFETTO_DISABLE_LOGGING"] = self.options.disable_logging
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["perfetto"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        if is_msvc(self):
            self.cpp_info.cxxflags.append("/Zc:__cplusplus")

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class SimdjsonConan(ConanFile):
    name = "simdjson"
    description = "Parsing gigabytes of JSON per second"
    license = ("Apache-2.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/simdjson"
    topics = ("json", "parser", "simd", "format")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if Version(self.version) < "3.12.0":
            self.license = "Apache-2.0"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _cmake_cxx_standard(self):
        compiler_cppstd = self.settings.get_safe("compiler.cppstd")
        if compiler_cppstd is None:
            return None
        if compiler_cppstd.startswith("gnu"):
            return compiler_cppstd[3:]
        return compiler_cppstd

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SIMDJSON_ENABLE_THREADS"] = self.options.threads
        tc.variables["SIMDJSON_DEVELOPER_MODE"] = False
        cppstd = self._cmake_cxx_standard
        if cppstd:
            tc.variables["SIMDJSON_CXX_STANDARD"] = cppstd
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "simdjson")
        self.cpp_info.set_property("cmake_target_name", "simdjson::simdjson")
        self.cpp_info.set_property("pkg_config_name", "simdjson")

        self.cpp_info.libs = ["simdjson"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        if self.options.threads:
            self.cpp_info.defines = ["SIMDJSON_THREADS_ENABLED=1"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
        if self.options.shared:
            self.cpp_info.defines.append("SIMDJSON_USING_LIBRARY=1")
            if is_msvc(self):
                self.cpp_info.defines.append("SIMDJSON_USING_WINDOWS_DYNAMIC_LIBRARY=1")

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.53.0"


class MuParserConan(ConanFile):
    name = "muparser"
    license = "BSD-2-Clause"
    homepage = "https://beltoforion.de/en/muparser/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("math", "parser",)
    description = "Fast Math Parser Library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.info.options.with_openmp:
            self.output.warn("Conan package for OpenMP is not available, this package will be used from system.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_SAMPLES"] = False
        tc.variables["ENABLE_OPENMP"] = self.options.with_openmp
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        license_file = "License.txt" if Version(self.version) < "2.3.3" else "LICENSE"
        copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "muparser")
        self.cpp_info.set_property("cmake_target_name", "muparser::muparser")
        self.cpp_info.set_property("pkg_config_name", "muparser")
        self.cpp_info.libs = ["muparser"]
        if not self.options.shared:
            self.cpp_info.defines = ["MUPARSER_STATIC=1"]
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

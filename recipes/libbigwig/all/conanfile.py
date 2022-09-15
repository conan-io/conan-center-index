from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, get, copy
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


class LibBigWigConan(ConanFile):
    name = "libbigwig"
    description = "A C library for handling bigWig files"
    topics = ("bioinformatics", "bigwig", "bigbed")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dpryan79/libBigWig"
    license = "MIT"
    settings = "arch", "build_type", "compiler", "os"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_curl": [True, False],
        "with_zlibng": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_curl": True,
        "with_zlibng": False
    }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_curl:
            self.requires("libcurl/7.84.0")
        if self.options.with_zlibng:
            self.requires("zlib-ng/2.0.6")
        else:
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Windows.")
        if self.info.options.with_zlibng:
            zlib_ng = self.dependencies["zlib-ng"]
            if not zlib_ng.options.zlib_compat:
                raise ConanInvalidConfiguration(f"{self.ref} requires the dependency option zlib-ng:zlib_compat=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTING"] = False
        tc.variables["WITH_CURL"] = self.options.with_curl
        tc.variables["WITH_ZLIBNG"] = self.options.with_zlibng
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW" # honor BUILD_SHARED_LIBS
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["BigWig"]
        self.cpp_info.system_libs = ["m"]
        self.cpp_info.set_property("cmake_file_name", "BigWig")
        self.cpp_info.set_property("cmake_target_name", "BigWig::BigWig")

        # TODO: Remove in Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "BigWig"
        self.cpp_info.names["cmake_find_package_multi"] = "BigWig"

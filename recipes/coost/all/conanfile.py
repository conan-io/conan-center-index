from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=1.50.0"


class CoostConan(ConanFile):
    name = "coost"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/idealvin/coost"
    license = "MIT"
    description = "A tiny boost library in C++11."
    topics = ("coroutine", "cpp11", "boost")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcurl": False,
        "with_openssl": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_libcurl:
            self.requires("libcurl/7.80.0")
        if self.options.with_libcurl or self.options.with_openssl:
            self.requires("openssl/1.1.1q")
    
    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.info.options.with_libcurl:
            if not self.info.options.with_openssl:
                raise ConanInvalidConfiguration(f"{self.name} requires with_openssl=True when using with_libcurl=True")
            if self.dependencies["libcurl"].options.with_ssl != "openssl":
                raise ConanInvalidConfiguration(f"{self.name} requires libcurl:with_ssl='openssl' to be enabled")
            if not self.dependencies["libcurl"].options.with_zlib:
                raise ConanInvalidConfiguration(f"{self.name} requires libcurl:with_zlib=True to be enabled")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["STATIC_VS_CRT"] = is_msvc_static_runtime(self)
        tc.variables["WITH_LIBCURL"] = self.options.with_libcurl
        tc.variables["WITH_OPENSSL"] = self.options.with_openssl
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "coost")
        self.cpp_info.set_property("cmake_target_name", "coost::co")
        # TODO: back to global scope in conan v2 once legacy generators removed
        self.cpp_info.components["co"].libs = ["co"]

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.components["co"].set_property("cmake_target_name", "coost::co")
        if self.options.with_libcurl:
            self.cpp_info.components["co"].requires.append("libcurl::libcurl")
        if self.options.with_libcurl or self.options.with_openssl:
            self.cpp_info.components["co"].requires.append("openssl::openssl")

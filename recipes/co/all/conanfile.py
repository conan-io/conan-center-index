import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc_static_runtime

required_conan_version = ">=1.53.0"


class CoConan(ConanFile):
    name = "co"
    description = "A go-style coroutine library in C++11 and more."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/idealvin/co"
    topics = ("coroutine", "c++11")

    package_type = "library"
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
    deprecated = "cocoyaxi"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libcurl:
            self.requires("libcurl/[>=7]")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.options.with_libcurl:
            if not self.options.with_openssl:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires with_openssl=True when using with_libcurl=True"
                )
            if self.options["libcurl"].with_ssl != "openssl":
                raise ConanInvalidConfiguration(
                    f"{self.name} requires libcurl:with_ssl='openssl' to be enabled"
                )
            if not self.options["libcurl"].with_zlib:
                raise ConanInvalidConfiguration(f"{self.name} requires libcurl:with_zlib=True to be enabled")

    def build_requirements(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            #  The OSX_ARCHITECTURES target property is now respected for the ASM language
            self.tool_requires("cmake/[>=3.20]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if not self.options.shared:
            tc.variables["FPIC"] = self.options.get_safe("fPIC", False)
        tc.variables["STATIC_VS_CRT"] = is_msvc_static_runtime(self)
        tc.variables["WITH_LIBCURL"] = self.options.with_libcurl
        tc.variables["WITH_OPENSSL"] = self.options.with_openssl
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["co"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]

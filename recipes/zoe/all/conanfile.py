from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class ZoeConan(ConanFile):
    name = "zoe"
    description = "A multi-protocol, multi-threaded, resumable, cross-platform, open source, C++ file download library."
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/winsoft666/zoe"
    topics = ("curl", "download", "file", "ftp", "multithreading", "http", "libcurl", "rate-limit")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

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
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True)

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.info.settings.compiler == "apple-clang" and Version(self.info.settings.compiler.version) < "12.0":
            raise ConanInvalidConfiguration(f"{self.ref} can not build on apple-clang < 12.0.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZOE_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["ZOE_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["ZOE_BUILD_TESTS"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        libname = "zoe" if self.options.shared else "zoe-static"
        libpostfix = "-d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"{libname}{libpostfix}"]

        if self.options.shared:
            self.cpp_info.defines.append("ZOE_EXPORTS")
        else:
            self.cpp_info.defines.append("ZOE_STATIC")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

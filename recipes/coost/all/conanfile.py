from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class CoostConan(ConanFile):
    name = "coost"
    description = "A tiny boost library in C++11."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/idealvin/coost"
    topics = ("coroutine", "cpp11", "boost")
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

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.with_libcurl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.with_libcurl or self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.settings.os == "Linux":
            self.requires("libbacktrace/cci.20210118")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if Version(self.version) >= "3.0.2" and is_msvc(self) and self.options.shared:
            # INFO: src\include\co\thread.h: error C2492: 'g_tid': data with thread storage duration may not have dll interface
            raise ConanInvalidConfiguration(f"{self.ref} Conan recipe does not support -o shared=True with Visual Studio. Contributions are welcome.")
        if self.info.options.with_libcurl:
            if not self.info.options.with_openssl:
                raise ConanInvalidConfiguration(f"{self.ref} requires with_openssl=True when using with_libcurl=True")
            if self.dependencies["libcurl"].options.with_ssl != "openssl":
                raise ConanInvalidConfiguration(f"{self.ref} requires libcurl/*:with_ssl='openssl' to be enabled")
            if not self.dependencies["libcurl"].options.with_zlib:
                raise ConanInvalidConfiguration(f"{self.ref} requires libcurl/*:with_zlib=True to be enabled")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["STATIC_VS_CRT"] = is_msvc_static_runtime(self)
        tc.variables["WITH_LIBCURL"] = self.options.with_libcurl
        tc.variables["WITH_OPENSSL"] = self.options.with_openssl
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

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
        self.cpp_info.libs = ["co"]

        self.cpp_info.set_property("cmake_file_name", "coost")
        self.cpp_info.set_property("cmake_target_name", "coost::co")
        self.cpp_info.set_property("pkg_config_name", "coost")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
        if self.settings.os == "Linux":
            self.cpp_info.requires.append("libbacktrace::libbacktrace")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class BeautyConan(ConanFile):
    name = "beauty"
    description = "HTTP Server above Boost.Beast"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dfleury2/beauty"
    topics = ("http", "server", "boost.beast")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/[>=1.78.0]", transitive_headers=True)
        if self.options.with_openssl:
            # dependency of asio in boost, exposed in boost/asio/ssl/detail/openssl_types.hpp
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)

        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} clang compiler requires -s compiler.libcxx=libc++")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BEAUTY_ENABLE_OPENSSL"] = self.options.with_openssl
        tc.cache_variables["BEAUTY_BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="beauty")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "beauty")
        self.cpp_info.set_property("cmake_target_name", "beauty::beauty")
        self.cpp_info.libs = ["beauty"]
        self.cpp_info.requires = ["boost::json"]
        if self.options.with_openssl:
            self.cpp_info.requires.append("openssl::ssl")
            self.cpp_info.defines = ["BEAUTY_ENABLE_OPENSSL"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32"]
            self.cpp_info.defines.append("_WIN32_WINNT=0xA00")
        if not self.options.shared:
            self.cpp_info.defines.append("BEAUTY_STATIC_DEFINE")

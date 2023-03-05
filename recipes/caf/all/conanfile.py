from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class CAFConan(ConanFile):
    name = "caf"
    description = "An open source implementation of the Actor Model in C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/actor-framework/actor-framework"
    topics = "actor-framework", "actor-model", "pattern-matching", "actors"
    license = "BSD-3-Clause", "BSL-1.0"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "log_level": ["error", "warning", "info", "debug", "trace", "quiet"],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "log_level": "quiet",
        "with_openssl": True,
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7",
            "clang": "6",   # Should be 5 but clang 5 has a bug that breaks compiling CAF
                            # see https://github.com/actor-framework/actor-framework/issues/1226
            "apple-clang": "10",
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
        if self.options.with_openssl:
            self.requires("openssl/1.1.1s")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) > "10.0" and \
           self.settings.arch == "x86":
            raise ConanInvalidConfiguration("clang >= 11.0 does not support x86")
        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows")
        if self.options.with_openssl and self.settings.os == "Windows" and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("OpenSSL is not supported for Windows x86")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.variables["CAF_ENABLE_OPENSSL_MODULE"] = self.options.with_openssl
        tc.variables["CAF_ENABLE_EXAMPLES"] = False
        tc.variables["CAF_ENABLE_TOOLS"] = False
        tc.variables["CAF_ENABLE_TESTING"] = False
        tc.variables["CAF_LOG_LEVEL"] = self.options.log_level.value.upper()
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CAF")

        self.cpp_info.components["caf_core"].set_property("cmake_target_name", "CAF::core")
        self.cpp_info.components["caf_core"].libs = ["caf_core"]
        if self.settings.os == "Windows":
            self.cpp_info.components["caf_core"].system_libs = ["iphlpapi"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["caf_core"].system_libs = ["pthread", "m"]

        self.cpp_info.components["caf_io"].set_property("cmake_target_name", "CAF::io")
        self.cpp_info.components["caf_io"].libs = ["caf_io"]
        self.cpp_info.components["caf_io"].requires = ["caf_core"]
        if self.settings.os == "Windows":
            self.cpp_info.components["caf_io"].system_libs = ["ws2_32"]

        if self.options.with_openssl:
            self.cpp_info.components["caf_openssl"].set_property("cmake_target_name", "CAF::openssl")
            self.cpp_info.components["caf_openssl"].libs = ["caf_openssl"]
            self.cpp_info.components["caf_openssl"].requires = ["caf_io", "openssl::openssl"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CAF"
        self.cpp_info.names["cmake_find_package_multi"] = "CAF"
        self.cpp_info.components["caf_core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["caf_core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["caf_io"].names["cmake_find_package"] = "io"
        self.cpp_info.components["caf_io"].names["cmake_find_package_multi"] = "io"
        if self.options.with_openssl:
            self.cpp_info.components["caf_openssl"].names["cmake_find_package"] = "openssl"
            self.cpp_info.components["caf_openssl"].names["cmake_find_package_multi"] = "openssl"

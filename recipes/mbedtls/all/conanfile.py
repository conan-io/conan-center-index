from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class MBedTLSConan(ConanFile):
    name = "mbedtls"
    description = (
        "mbed TLS makes it trivially easy for developers to include "
        "cryptographic and SSL/TLS capabilities in their (embedded) products"
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tls.mbed.org"
    topics = ("polarssl", "tls", "security")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "enable_threading": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "enable_threading": False,
    }
    implements = ["auto_shared_fpic"]

    def config_options(self):
        if Version(self.version) >= "3.0.0":
            # ZLIB support has been ditched on version 3.0.0
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.settings.os == "Windows":
            if self.options.enable_threading:
                # INFO: Planned: https://github.com/Mbed-TLS/mbedtls/issues/8455
                raise ConanInvalidConfiguration(f"{self.ref} does not support the option enable_threading on Windows")

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            # The command line flags set are not supported on older versions of gcc
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support {self.settings.compiler}-{self.settings.compiler.version}"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_SHARED_MBEDTLS_LIBRARY"] = bool(self.options.shared)
        tc.cache_variables["USE_STATIC_MBEDTLS_LIBRARY"] = not bool(self.options.shared)
        if Version(self.version) < "3.0.0":
            tc.cache_variables["ENABLE_ZLIB_SUPPORT"] = self.options.with_zlib
        tc.cache_variables["ENABLE_PROGRAMS"] = False
        tc.cache_variables["MBEDTLS_FATAL_WARNINGS"] = False
        tc.cache_variables["ENABLE_TESTING"] = False
        if Version(self.version) < "3.0.0":
            # relocatable shared libs on macOS
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        if is_msvc(self):
            if self.options.shared:
                tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
                replace_in_file(self, os.path.join(self.source_folder, "library", "constant_time_impl.h"), "extern volatile", "__declspec(dllimport) volatile")
                replace_in_file(self, os.path.join(self.source_folder, "include", "mbedtls", "x509_crt.h"), "extern const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_suiteb;", "__declspec(dllimport) const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_suiteb;")
                replace_in_file(self, os.path.join(self.source_folder, "include", "mbedtls", "x509_crt.h"), "extern const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_default;", "__declspec(dllimport) const mbedtls_x509_crt_profile mbedtls_x509_crt_profile_default;")
                replace_in_file(self, os.path.join(self.source_folder, "library", "psa_util_internal.h"), "extern const mbedtls_error_pair_t psa_to_ssl_errors[7];", "__declspec(dllimport) const mbedtls_error_pair_t psa_to_ssl_errors[7];")
            if check_min_vs(self, 190, raise_invalid=False):
                tc.preprocessor_definitions["MBEDTLS_PLATFORM_SNPRINTF_MACRO"] = "snprintf"
            else:
                tc.preprocessor_definitions["MBEDTLS_PLATFORM_SNPRINTF_MACRO"] = "MBEDTLS_PLATFORM_STD_SNPRINTF"
        if self.options.enable_threading:
            tc.preprocessor_definitions["MBEDTLS_THREADING_C"] = True
            tc.preprocessor_definitions["MBEDTLS_THREADING_PTHREAD"] = True

        tc.generate()
        tc = CMakeDeps(self)
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
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MbedTLS")
        self.cpp_info.set_property("cmake_target_name", "MbedTLS::mbedtls")

        self.cpp_info.components["mbedcrypto"].set_property("cmake_target_name", "MbedTLS::mbedcrypto")
        self.cpp_info.components["mbedcrypto"].libs = ["mbedcrypto"]
        if self.settings.os == "Windows":
            self.cpp_info.components["mbedcrypto"].system_libs = ["bcrypt"]
        if Version(self.version) >= "3.6.0":
            self.cpp_info.components["mbedcrypto"].set_property("pkg_config_name", "mbedcrypto")
        if self.options.enable_threading:
            self.cpp_info.components["mbedcrypto"].defines.extend(["MBEDTLS_THREADING_C=1", "MBEDTLS_THREADING_PTHREAD=1"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["mbedcrypto"].system_libs.append("pthread")

        self.cpp_info.components["mbedx509"].set_property("cmake_target_name", "MbedTLS::mbedx509")
        self.cpp_info.components["mbedx509"].libs = ["mbedx509"]
        if self.settings.os == "Windows":
            self.cpp_info.components["mbedx509"].system_libs = ["ws2_32"]
        self.cpp_info.components["mbedx509"].requires = ["mbedcrypto"]
        if Version(self.version) >= "3.6.0":
            self.cpp_info.components["mbedx509"].set_property("pkg_config_name", "mbedx509")

        self.cpp_info.components["libembedtls"].set_property("cmake_target_name", "MbedTLS::mbedtls")
        self.cpp_info.components["libembedtls"].libs = ["mbedtls"]
        self.cpp_info.components["libembedtls"].requires = ["mbedx509"]
        if Version(self.version) >= "3.6.0":
            self.cpp_info.components["libembedtls"].set_property("pkg_config_name", "embedtls")

        if self.options.get_safe("with_zlib"):
            for component in self.cpp_info.components:
                self.cpp_info.components[component].requires.append("zlib::zlib")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        #self.cpp_info.names["cmake_find_package"] = "MbedTLS"
        #self.cpp_info.names["cmake_find_package_multi"] = "MbedTLS"
        self.cpp_info.components["libembedtls"].names["cmake_find_package"] = "mbedtls"
        self.cpp_info.components["libembedtls"].names["cmake_find_package_multi"] = "mbedtls"

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class MBedTLSConan(ConanFile):
    name = "mbedtls"
    description = (
        "mbed TLS makes it trivially easy for developers to include "
        "cryptographic and SSL/TLS capabilities in their (embedded) products"
    )
    topics = ("polarssl", "tls", "security")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tls.mbed.org"
    license = ("GPL-2.0", "Apache-2.0",)

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
    }

    @property
    def _license(self):
        return self.version.rsplit("-", 1)[1]

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "3.0.0":
            # ZLIB support has been ditched on version 3.0.0
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        if Version(self.version) >= "2.23.0":
            self.license = "Apache-2.0"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.13")

    def validate(self):
        if Version(self.version) >= "2.23.0":
            if self.info.settings.os == "Windows" and self.info.options.shared:
                raise ConanInvalidConfiguration(f"{self.ref} does not support shared build on Windows")

            if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < "5":
                # The command line flags set are not supported on older versions of gcc
                raise ConanInvalidConfiguration(
                    f"{self.ref} does not support {self.info.settings.compiler}-{self.info.settings.compiler.version}"
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root = True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_SHARED_MBEDTLS_LIBRARY"] = self.options.shared
        tc.variables["USE_STATIC_MBEDTLS_LIBRARY"] = not self.options.shared
        if Version(self.version) < "3.0.0":
            tc.variables["ENABLE_ZLIB_SUPPORT"] = self.options.with_zlib
        tc.variables["ENABLE_PROGRAMS"] = False
        if Version(self.version) >= "2.23.0":
            tc.variables["MBEDTLS_FATAL_WARNINGS"] = False
        tc.variables["ENABLE_TESTING"] = False
        if Version(self.version) < "3.0.0":
            # relocatable shared libs on macOS
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "2.23.0":
            # No warnings as errors
            cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
            replace_in_file(self, cmakelists, "-Werror", "")
            replace_in_file(self, cmakelists, "/WX", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if Version(self.version) < "2.23.0": # less then 2.23 is multi-licensed
            license = "gpl-2.0.txt" if self._license == "gpl" else "apache-2.0.txt"
            copy(self, license, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MbedTLS")
        self.cpp_info.set_property("cmake_target_name", "MbedTLS::mbedtls")

        self.cpp_info.components["mbedcrypto"].set_property("cmake_target_name", "MbedTLS::mbedcrypto")
        self.cpp_info.components["mbedcrypto"].libs = ["mbedcrypto"]

        self.cpp_info.components["mbedx509"].set_property("cmake_target_name", "MbedTLS::mbedx509")
        self.cpp_info.components["mbedx509"].libs = ["mbedx509"]
        self.cpp_info.components["mbedx509"].requires = ["mbedcrypto"]

        self.cpp_info.components["libembedtls"].set_property("cmake_target_name", "MbedTLS::mbedtls")
        self.cpp_info.components["libembedtls"].libs = ["mbedtls"]
        self.cpp_info.components["libembedtls"].requires = ["mbedx509"]

        if self.options.get_safe("with_zlib"):
            for component in self.cpp_info.components:
                self.cpp_info.components[component].requires.append("zlib::zlib")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "MbedTLS"
        self.cpp_info.names["cmake_find_package_multi"] = "MbedTLS"
        self.cpp_info.components["libembedtls"].names["cmake_find_package"] = "mbedtls"
        self.cpp_info.components["libembedtls"].names["cmake_find_package_multi"] = "mbedtls"

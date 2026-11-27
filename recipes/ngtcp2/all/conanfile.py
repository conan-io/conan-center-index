import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir, copy
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout

required_conan_version = ">=1.54.0"

class NgTcp2Conan(ConanFile):
    name = "ngtcp2"
    description = "ngtcp2 project is an effort to implement IETF QUIC protocol"
    license = "MIT"
    homepage = "https://github.com/ngtcp2/ngtcp2"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("networking", "network", "quic", "udp", "protocol", "rfc9000")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "enable_openssl": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "enable_openssl": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.get_safe("enable_openssl", False):
            self.requires("openssl/3.6.5")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_LIB_ONLY"] = True
        if self.options.enable_openssl:
            tc.cache_variables["ENABLE_OPENSSL"] = True
            tc.cache_variables["HAVE_SSL_SET_QUIC_TLS_CBS"] = True
        if self.options.shared:
            tc.cache_variables["ENABLE_SHARED_LIB"] = True
            tc.cache_variables["ENABLE_STATIC_LIB"] = False
        else:
            tc.cache_variables["ENABLE_SHARED_LIB"] = False
            tc.cache_variables["ENABLE_STATIC_LIB"] = True

        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["ngtcp2"].libs = ["ngtcp2"]

        if self.options.enable_openssl:
            self.cpp_info.components["crypto_ossl"].libs = ["ngtcp2_crypto_ossl"]
            self.cpp_info.components["crypto_ossl"].requires = ["ngtcp2"]

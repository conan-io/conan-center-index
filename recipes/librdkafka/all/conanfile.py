from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.47.0"


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    description = (
        "Librdkafka is an Apache Kafka C/C++ library designed with message "
        "delivery reliability and high performance in mind."
    )
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/edenhill/librdkafka"
    topics = ("kafka", "consumer", "producer")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "zlib": [True, False],
        "zstd": [True, False],
        "plugins": [True, False],
        "ssl": [True, False],
        "sasl": [True, False],
        "curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zlib": False,
        "zstd": False,
        "plugins": False,
        "ssl": False,
        "sasl": False,
        "curl": False,
    }

    generators = "CMakeDeps", "PkgConfigDeps"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.9.0":
            del self.options.curl

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("lz4/1.9.3")
        if self.options.zlib:
            self.requires("zlib/1.2.12")
        if self.options.zstd:
            self.requires("zstd/1.5.2")
        if self.options.ssl:
            self.requires("openssl/1.1.1q")
        if self.options.sasl and self.settings.os != "Windows":
            self.requires("cyrus-sasl/2.1.27")
        if self.options.get_safe("curl", False):
            self.requires("libcurl/7.84.0")

    def build_requirements(self):
        if self.options.sasl and self.settings.os != "Windows":
            self.build_requires("pkgconf/1.7.4")

    def layout(self):
        cmake_layout(self)
        self.folders.source = "src"
        self.folders.build = "build"

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITHOUT_OPTIMIZATION"] = self.settings.build_type == "Debug"
        tc.variables["ENABLE_DEVEL"] = self.settings.build_type == "Debug"
        tc.variables["RDKAFKA_BUILD_STATIC"] = not self.options.shared
        tc.variables["RDKAFKA_BUILD_EXAMPLES"] = False
        tc.variables["RDKAFKA_BUILD_TESTS"] = False
        tc.variables["WITHOUT_WIN32_CONFIG"] = True
        tc.variables["WITH_BUNDLED_SSL"] = False
        tc.variables["WITH_ZLIB"] = self.options.zlib
        tc.variables["WITH_ZSTD"] = self.options.zstd
        tc.variables["WITH_PLUGINS"] = self.options.plugins
        tc.variables["WITH_SSL"] = self.options.ssl
        tc.variables["WITH_SASL"] = self.options.sasl
        tc.variables["ENABLE_LZ4_EXT"] = True
        if Version(self.version) >= "1.9.0":
            tc.variables["WITH_CURL"] = self.options.curl
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSES.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "RdKafka")
        # Avoid to create undesirables librdkafka::librdkafka target and librdkafka.pc
        # it's fine since rdkafka++ component depends on all components
        self.cpp_info.set_property("cmake_target_name", "RdKafka::rdkafka++")
        self.cpp_info.set_property("pkg_config_name", "rdkafka++")

        # rdkafka
        self.cpp_info.components["rdkafka"].set_property("cmake_target_name", "RdKafka::rdkafka")
        self.cpp_info.components["rdkafka"].set_property("pkg_config_name", "rdkafka")
        self.cpp_info.components["rdkafka"].libs = ["rdkafka"]
        self.cpp_info.components["rdkafka"].requires = ["lz4::lz4"]
        if self.options.zlib:
            self.cpp_info.components["rdkafka"].requires.append("zlib::zlib")
        if self.options.zstd:
            self.cpp_info.components["rdkafka"].requires.append("zstd::zstd")
        if self.options.ssl:
            self.cpp_info.components["rdkafka"].requires.append("openssl::openssl")
        if self.options.sasl and self.settings.os != "Windows":
            self.cpp_info.components["rdkafka"].requires.append("cyrus-sasl::cyrus-sasl")
        if self.options.get_safe("curl", False):
            self.cpp_info.components["rdkafka"].requires.append("libcurl::libcurl")
        if self.settings.os == "Windows":
            self.cpp_info.components["rdkafka"].system_libs = ["ws2_32", "secur32"]
            if self.options.ssl:
                self.cpp_info.components["rdkafka"].system_libs.append("crypt32")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["rdkafka"].system_libs.extend(["pthread", "rt", "dl", "m"])
        if not self.options.shared:
            self.cpp_info.components["rdkafka"].defines.append("LIBRDKAFKA_STATICLIB")

        # rdkafka++
        self.cpp_info.components["rdkafka++"].set_property("cmake_target_name", "RdKafka::rdkafka++")
        self.cpp_info.components["rdkafka++"].set_property("pkg_config_name", "rdkafka++")
        self.cpp_info.components["rdkafka++"].libs = ["rdkafka++"]
        self.cpp_info.components["rdkafka++"].requires = ["rdkafka"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "RdKafka"
        self.cpp_info.names["cmake_find_package_multi"] = "RdKafka"

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.43.0"


class CivetwebConan(ConanFile):
    name = "civetweb"
    license = "MIT"
    homepage = "https://github.com/civetweb/civetweb"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Embedded C/C++ web server"
    topics = ("civetweb", "web-server", "embedded")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "ssl_dynamic_loading": [True, False],
        "with_caching": [True, False],
        "with_cgi": [True, False],
        "with_cxx": [True, False],
        "with_duktape": [True, False],
        "with_ipv6": [True, False],
        "with_lua": [True, False],
        "with_server_stats": [True, False],
        "with_ssl": [True, False],
        "with_static_files": [True, False],
        "with_third_party_output": [True, False],
        "with_websockets": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "ssl_dynamic_loading": False,
        "with_caching": True,
        "with_cgi": True,
        "with_cxx": True,
        "with_duktape": False,
        "with_ipv6": True,
        "with_lua": False,
        "with_server_stats": False,
        "with_ssl": True,
        "with_static_files": True,
        "with_third_party_output": False,
        "with_websockets": True,
        "with_zlib": False,
    }

    no_copy_source = True

    @property
    def _has_zlib_option(self):
        return Version(self.version) >= "1.15"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, patch["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_zlib_option:
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_cxx:
            del self.settings.compiler.cppstd
            del self.settings.compiler.libcxx
        if not self.options.with_ssl:
            del self.options.ssl_dynamic_loading

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1n")
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.options.get_safe("ssl_dynamic_loading") and not self.options["openssl"].shared:
            raise ConanInvalidConfiguration("ssl_dynamic_loading requires shared openssl")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)

        if self.options.with_ssl:
            openssl_version = Version(self.dependencies["openssl"].ref.version[:-1])
            tc.variables["CIVETWEB_ENABLE_SSL"] = self.options.with_ssl
            tc.variables["CIVETWEB_ENABLE_SSL_DYNAMIC_LOADING"] = self.options.ssl_dynamic_loading
            tc.variables["CIVETWEB_SSL_OPENSSL_API_1_0"] = openssl_version.minor == "0"
            tc.variables["CIVETWEB_SSL_OPENSSL_API_1_1"] = openssl_version.minor == "1"

        tc.variables["CIVETWEB_BUILD_TESTING"] = False
        tc.variables["CIVETWEB_CXX_ENABLE_LTO"] = False
        tc.variables["CIVETWEB_ENABLE_ASAN"] = False

        tc.variables["CIVETWEB_DISABLE_CACHING"] = not self.options.with_caching
        tc.variables["CIVETWEB_DISABLE_CGI"] = not self.options.with_cgi
        tc.variables["CIVETWEB_ENABLE_CXX"] = self.options.with_cxx
        tc.variables["CIVETWEB_ENABLE_DUKTAPE"] = self.options.with_duktape
        tc.variables["CIVETWEB_ENABLE_IPV6"] = self.options.with_ipv6
        tc.variables["CIVETWEB_ENABLE_LUA"] = self.options.with_lua
        tc.variables["CIVETWEB_ENABLE_SERVER_STATS"] = self.options.with_server_stats
        tc.variables["CIVETWEB_ENABLE_THIRD_PARTY_OUTPUT"] = self.options.with_third_party_output
        tc.variables["CIVETWEB_ENABLE_WEBSOCKETS"] = self.options.with_websockets
        tc.variables["CIVETWEB_SERVE_NO_FILES"] = not self.options.with_static_files

        if self._has_zlib_option:
            tc.variables["CIVETWEB_ENABLE_ZLIB"] = self.options.with_zlib

        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        bin_folder = os.path.join(self.package_folder, "bin")
        for bin_file in os.listdir(bin_folder):
            if not bin_file.startswith("civetweb"):
                os.remove(os.path.join(bin_folder, bin_file))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "civetweb"
        self.cpp_info.names["cmake_find_package_multi"] = "civetweb"
        self.cpp_info.set_property("cmake_file_name", "civetweb")
        self.cpp_info.set_property("cmake_target_name", "civetweb::civetweb")
        self.cpp_info.components["_civetweb"].names["cmake_find_package"] = "civetweb"
        self.cpp_info.components["_civetweb"].names["cmake_find_package_multi"] = "civetweb"
        self.cpp_info.components["_civetweb"].set_property("cmake_target_name", "civetweb::civetweb")
        self.cpp_info.components["_civetweb"].libs = ["civetweb"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_civetweb"].system_libs.extend(["rt", "pthread"])
            if self.options.get_safe("ssl_dynamic_loading"):
                self.cpp_info.components["_civetweb"].system_libs.append("dl")
        elif self.settings.os == "Macos":
            self.cpp_info.components["_civetweb"].frameworks.append("Cocoa")
        elif self.settings.os == "Windows":
            self.cpp_info.components["_civetweb"].system_libs.append("ws2_32")
            if self.options.shared:
                self.cpp_info.components["_civetweb"].defines.append("CIVETWEB_DLL_IMPORTS")

        if self.options.with_ssl:
            self.cpp_info.components["_civetweb"].requires.append("openssl::openssl")
        if self.options.get_safe("with_zlib"):
            self.cpp_info.components["_civetweb"].requires.append("zlib::zlib")

        if self.options.with_cxx:
            self.cpp_info.components["civetweb-cpp"].names["cmake_find_package"] = "civetweb-cpp"
            self.cpp_info.components["civetweb-cpp"].names["cmake_find_package_multi"] = "civetweb-cpp"
            self.cpp_info.components["civetweb-cpp"].set_property("cmake_target_name", "civetweb::civetweb-cpp")
            self.cpp_info.components["civetweb-cpp"].libs = ["civetweb-cpp"]
            self.cpp_info.components["civetweb-cpp"].requires = ["_civetweb"]
            if self.settings.os == "Linux":
                self.cpp_info.components["civetweb-cpp"].system_libs.append("m")
            elif self.settings.os == "Windows":
                if self.options.shared:
                    self.cpp_info.components["civetweb-cpp"].defines.append("CIVETWEB_CXX_DLL_IMPORTS")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

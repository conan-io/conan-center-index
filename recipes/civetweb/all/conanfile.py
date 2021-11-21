import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class CivetwebConan(ConanFile):
    name = "civetweb"
    license = "MIT"
    homepage = "https://github.com/civetweb/civetweb"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Embedded C/C++ web server"
    topics = ("conan", "civetweb", "web-server", "embedded")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared"            : [True, False],
        "fPIC"              : [True, False],
        "with_ssl"        : [True, False],
        "ssl_dynamic_loading": [True, False],
        "with_websockets" : [True, False],
        "with_ipv6"       : [True, False],
        "with_cxx"        : [True, False]
    }
    default_options = {
        "shared"            : False,
        "fPIC"              : True,
        "with_ssl"        : True,
        "ssl_dynamic_loading": False,
        "with_websockets" : True,
        "with_ipv6"       : True,
        "with_cxx"        : True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

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
            self.requires("openssl/1.1.1l")

    def validate(self):
        if self.options.get_safe("ssl_dynamic_loading") and not self.options["openssl"].shared:
            raise ConanInvalidConfiguration("ssl_dynamic_loading requires shared openssl")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CIVETWEB_ENABLE_SSL"] = self.options.with_ssl
        if self.options.with_ssl:
            openssl_version = tools.Version(self.deps_cpp_info["openssl"].version[:-1])
            self._cmake.definitions["CIVETWEB_SSL_OPENSSL_API_1_0"] = openssl_version.minor == "0"
            self._cmake.definitions["CIVETWEB_SSL_OPENSSL_API_1_1"] = openssl_version.minor == "1"
            self._cmake.definitions["CIVETWEB_ENABLE_SSL_DYNAMIC_LOADING"] = self.options.ssl_dynamic_loading
        self._cmake.definitions["CIVETWEB_ENABLE_WEBSOCKETS"] = self.options.with_websockets
        self._cmake.definitions["CIVETWEB_ENABLE_IPV6"] = self.options.with_ipv6
        self._cmake.definitions["CIVETWEB_ENABLE_CXX"] = self.options.with_cxx
        self._cmake.definitions["CIVETWEB_BUILD_TESTING"] = False
        self._cmake.definitions["CIVETWEB_ENABLE_ASAN"] = False
        self._cmake.definitions["CIVETWEB_CXX_ENABLE_LTO"] = False
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(os.path.join(self._source_subfolder, "LICENSE.md"), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        bin_folder = os.path.join(self.package_folder, "bin")
        for bin_file in os.listdir(bin_folder):
            if not bin_file.startswith("civetweb"):
                os.remove(os.path.join(bin_folder, bin_file))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "civetweb"
        self.cpp_info.names["cmake_find_package_multi"] = "civetweb"
        self.cpp_info.components["_civetweb"].names["cmake_find_package"] = "civetweb"
        self.cpp_info.components["_civetweb"].names["cmake_find_package_multi"] = "civetweb"
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
            self.cpp_info.components["_civetweb"].requires = ["openssl::openssl"]

        if self.options.with_cxx:
            self.cpp_info.components["civetweb-cpp"].names["cmake_find_package"] = "civetweb-cpp"
            self.cpp_info.components["civetweb-cpp"].names["cmake_find_package_multi"] = "civetweb-cpp"
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

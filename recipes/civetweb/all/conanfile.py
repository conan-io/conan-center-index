import os
from conans import ConanFile, tools, CMake

class civetwebConan(ConanFile):
    name = "civetweb"
    license = "MIT"
    homepage = "https://github.com/civetweb/civetweb"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Embedded C/C++ web server"
    topics = ("conan", "civetweb", "web-server", "embedded")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared"            : [True, False],
        "fPIC"              : [True, False],
        "with_ssl"        : [True, False],
        "with_websockets" : [True, False],
        "with_ipv6"       : [True, False],
        "with_cxx"        : [True, False]
    }
    default_options = {
        "shared"            : False,
        "fPIC"              : True,
        "with_ssl"        : True,
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
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if not self.options.with_cxx:
            del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1i")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CIVETWEB_ENABLE_SSL"] = self.options.with_ssl
        self._cmake.definitions["CIVETWEB_ENABLE_WEBSOCKETS"] = self.options.with_websockets
        self._cmake.definitions["CIVETWEB_ENABLE_IPV6"] = self.options.with_ipv6
        self._cmake.definitions["CIVETWEB_ENABLE_CXX"] = self.options.with_cxx
        self._cmake.definitions["CIVETWEB_BUILD_TESTING"] = False
        self._cmake.definitions["CIVETWEB_ENABLE_ASAN"] = False
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("civetweb-%s" % self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(os.path.join(self._source_subfolder, "LICENSE.md"), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        bin_folder = os.path.join(self.package_folder, "bin");
        for bin_file in os.listdir(bin_folder):
            if not bin_file.startswith("civetweb"):
                os.remove(os.path.join(bin_folder, bin_file))

    def package_info(self):
        self.cpp_info.components["_civetweb"].names["cmake_find_package"] = "civetweb"
        self.cpp_info.components["_civetweb"].names["cmake_find_package_multi"] = "civetweb"
        self.cpp_info.components["_civetweb"].names["pkg_config"] = "civetweb"
        self.cpp_info.components["_civetweb"].libs = ["civetweb"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_civetweb"].system_libs.extend(["dl", "rt", "pthread"])
        elif self.settings.os == "Macos":
            self.cpp_info.components["_civetweb"].frameworks.append("Cocoa")
            self.cpp_info.components["_civetweb"].defines.append("USE_COCOA")
        elif self.settings.os == "Windows":
            self.cpp_info.components["_civetweb"].system_libs .append("ws2_32")
        if self.options.with_websockets:
            self.cpp_info.components["_civetweb"].defines.append("USE_WEBSOCKET")
        if self.options.with_ipv6:
            self.cpp_info.components["_civetweb"].defines.append("USE_IPV6")
        if self.options.with_ssl:
            self.cpp_info.components["_civetweb"].requires = ["openssl::ssl"]
        else:
            self.cpp_info.components["_civetweb"].defines.append("NO_SSL")

        if self.options.with_cxx:
            self.cpp_info.components["civetweb-cpp"].names["cmake_find_package"] = "civetweb-cpp"
            self.cpp_info.components["civetweb-cpp"].names["cmake_find_package_multi"] = "civetweb-cpp"
            self.cpp_info.components["civetweb-cpp"].names["pkg_config"] = "civetweb-cpp"
            self.cpp_info.components["civetweb-cpp"].libs = ["civetweb-cpp"]
            self.cpp_info.components["civetweb-cpp"].requires = ["_civetweb"]
            if self.settings.os == "Linux":
                self.cpp_info.components["civetweb-cpp"].system_libs.append("m")

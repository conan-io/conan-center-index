from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class MiniupnpcConan(ConanFile):
    name = "miniupnpc"
    description = "UPnP client library/tool to access Internet Gateway Devices."
    license = "BSD-3-Clause"
    topics = ("miniupnpc", "upnp", "networking", "internet-gateway")
    homepage = "https://github.com/miniupnp/miniupnp"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Do not force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "miniupnpc", "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["UPNPC_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["UPNPC_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["UPNPC_BUILD_TESTS"] = False
        self._cmake.definitions["UPNPC_BUILD_SAMPLE"] = False
        self._cmake.definitions["NO_GETADDRINFO"] = False
        self._cmake.definitions["UPNPC_NO_INSTALL"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "miniupnpc"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "miniupnpc"
        self.cpp_info.names["cmake_find_package_multi"] = "miniupnpc"
        self.cpp_info.names["pkg_config"] = "miniupnpc"
        prefix = "lib" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["{}miniupnpc".format(prefix)]
        if not self.options.shared:
            self.cpp_info.defines.append("MINIUPNP_STATICLIB")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "ws2_32"]
        elif self.settings.os == "SunOS":
            self.cpp_info.system_libs = ["socket", "nsl", "resolv"]

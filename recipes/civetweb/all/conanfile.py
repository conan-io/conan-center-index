from conans import ConanFile, tools, CMake
import os

class civetwebConan(ConanFile):
    name = "civetweb"
    license = "MIT"
    homepage = "https://github.com/civetweb/civetweb"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Embedded C/C++ web server"
    topics = ("conan", "civetweb", "web-server", "embedded")
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
        cmake = CMake(self)
        cmake.verbose = True
        cmake.definitions["CIVETWEB_ENABLE_SSL"] = self.options.with_ssl
        cmake.definitions["CIVETWEB_ENABLE_WEBSOCKETS"] = self.options.with_websockets
        cmake.definitions["CIVETWEB_ENABLE_IPV6"] = self.options.with_ipv6
        cmake.definitions["CIVETWEB_ENABLE_CXX"] = self.options.with_cxx
        cmake.definitions["CIVETWEB_BUILD_TESTING"] = False
        cmake.definitions["CIVETWEB_ENABLE_ASAN"] = False
        cmake.configure(
                source_dir=os.path.relpath(self._source_subfolder, self._build_subfolder),
                build_dir=self._build_subfolder)
        return cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("civetweb-%s" % self.version, self._source_subfolder)
        tools.replace_in_file(file_path=os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              search="project (civetweb)",
                              replace="""project (civetweb)
                                 include(../conanbuildinfo.cmake)
                                 conan_basic_setup()""")

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
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "rt", "pthread"])
            if self.options.with_cxx:
                self.cpp_info.libs.append("m")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Cocoa")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
            self.cpp_info.defines.append("USE_COCOA")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs .append("ws2_32")
        if self.options.with_websockets:
            self.cpp_info.defines.append("USE_WEBSOCKET")
        if self.options.with_ipv6:
            self.cpp_info.defines.append("USE_IPV6")
        if not self.options.with_ssl:
            self.cpp_info.defines.append("NO_SSL")

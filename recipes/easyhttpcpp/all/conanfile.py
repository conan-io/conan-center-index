from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os


class EasyhttpcppConan(ConanFile):
    name = "easyhttpcpp"
    description = "A cross-platform HTTP client library with a focus on usability and speed"
    license = ("MIT",)
    topics = ("conan", "easyhttpcpp", "http", "client", "protocol")
    homepage = "https://github.com/sony/easyhttpcpp"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def requirements(self):
        self.requires("poco/1.10.1")
        if self.settings.os != "Windows":
            self.requires("openssl/1.1.1g")

    @property
    def _required_poco_components(self):
        comps = ["enable_data", "enable_data_sqlite", "enable_net"]
        if self.settings.os == "Windows":
            comps.append("enable_netssl_win")
        else:
            comps.append("enable_netssl")
        return comps

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FORCE_SHAREDLIB"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"].get(self.version, []):
            tools.patch(**patch)

    def build(self):
        for comp in self._required_poco_components:
            if not getattr(self.options["poco"], comp):
                raise ConanInvalidConfiguration("{} requires the following poco option enabled: '{}'".format(self.name, comp))

        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        libsuffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                if not self.options.shared:
                    libsuffix += "md"
            libsuffix += "d"
        self.cpp_info.libs = ["easyhttp{}".format(libsuffix)]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("EASYHTTPCPP_DLL")
        self.cpp_info.names["cmake_find_package"] = "easyhttpcppeasyhttp"
        self.cpp_info.names["cmake_find_package_multi"] = "easyhttpcppeasyhttp"

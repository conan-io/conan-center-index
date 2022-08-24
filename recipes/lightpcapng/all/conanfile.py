from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

class LightPcapNgConan(ConanFile):
    name = "lightpcapng"
    homepage = "https://github.com/Technica-Engineering/LightPcapNg"
    description = "Library for general-purpose tracing based on PCAPNG file format"
    topics = ("pcapng", "pcap")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zstd": True,
    }
    generators = "cmake", "cmake_paths", "cmake_find_package"
    exports_sources = "CMakeLists.txt"
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
        if self.options.with_zstd:
            self.options["zstd"].shared = self.options.shared
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zstd:
            self.requires("zstd/1.4.5")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIGHT_USE_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "light_pcapng"
        self.cpp_info.names["cmake_find_package_multi"] = "light_pcapng"
        self.cpp_info.components["liblight_pcapng"].names["cmake_find_package"] = "light_pcapng"
        self.cpp_info.components["liblight_pcapng"].names["cmake_find_package_multi"] = "light_pcapng"
        self.cpp_info.components["liblight_pcapng"].libs = ["light_pcapng"]

        if self.options.with_zstd:
            self.cpp_info.components["liblight_pcapng"].requires = ["zstd::zstd"]


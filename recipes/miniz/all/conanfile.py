from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class MinizConan(ConanFile):
    name = "miniz"
    description = "Lossless, high performance data compression library that " \
                  "implements the zlib (RFC 1950) and Deflate (RFC 1951) " \
                  "compressed data format specification standards"
    license = "MIT"
    topics = ("conan", "miniz", "compression", "lossless")
    homepage = "https://github.com/richgel999/miniz"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) >= "2.2.0":
            self._cmake.definitions["BUILD_EXAMPLES"] = False
            self._cmake.definitions["BUILD_FUZZERS"] = False
            self._cmake.definitions["AMALGAMATE_SOURCES"] = False
            self._cmake.definitions["BUILD_HEADER_ONLY"] = False
            self._cmake.definitions["INSTALL_PROJECT"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "miniz"
        self.cpp_info.names["cmake_find_package_multi"] = "miniz"
        self.cpp_info.names["pkg_config"] = "miniz"
        self.cpp_info.libs = ["miniz"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "miniz")]

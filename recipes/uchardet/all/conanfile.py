from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class UchardetConan(ConanFile):
    name = "uchardet"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/freedesktop/uchardet"
    description = "uchardet is an encoding detector library, which takes a sequence of bytes in an unknown character encoding and attempts to determine the encoding of the text. Returned encoding names are iconv-compatible."
    topics = ("conan", "encoding", "detector")
    license = "MPL 1.1"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "check_sse2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "check_sse2": True,
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${CMAKE_BINARY_DIR}/uchardet.pc",
                              "${CMAKE_CURRENT_BINARY_DIR}/uchardet.pc")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["CHECK_SSE2"] = self.options.check_sse2
        self._cmake.definitions["BUILD_BINARY"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "uchardet"
        self.cpp_info.names["cmake_find_package_multi"] = "uchardet"
        self.cpp_info.names["pkgconfig"] = "libuchardet"
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["uchardet" + postfix]

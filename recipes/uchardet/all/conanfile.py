from conan import ConanFile, tools
from conans import CMake
import os
import functools

required_conan_version = ">=1.33.0"


class UchardetConan(ConanFile):
    name = "uchardet"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/freedesktop/uchardet"
    description = "uchardet is an encoding detector library, which takes a sequence of bytes in an unknown character encoding and attempts to determine the encoding of the text. Returned encoding names are iconv-compatible."
    topics = "encoding", "detector"
    license = "MPL-1.1"

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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self._settings_build not in ("x86", "x86_64"):
            del self.options.check_sse2
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # the following fixes that apply to uchardet version 0.0.7
        # fix broken cmake
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "${CMAKE_BINARY_DIR}",
            "${CMAKE_CURRENT_BINARY_DIR}")
        # fix problem with mac os
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            'string(TOLOWER ${CMAKE_SYSTEM_PROCESSOR} TARGET_ARCHITECTURE)',
            'string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" TARGET_ARCHITECTURE)')
        # disable building tests
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "add_subdirectory(test)",
            "#add_subdirectory(test)")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CHECK_SSE2"] = self.options.get_safe("check_sse2", False)
        cmake.definitions["BUILD_BINARY"] = False
        cmake.definitions["BUILD_STATIC"] = False  # disable building static libraries when self.options.shared is True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "uchardet")
        self.cpp_info.set_property("cmake_target_name", "uchardet")
        self.cpp_info.set_property("pkg_config_name", "libuchardet")

        self.cpp_info.names["cmake_find_package"] = "uchardet"
        self.cpp_info.names["cmake_find_package_multi"] = "uchardet"
        self.cpp_info.names["pkgconfig"] = "libuchardet"
        self.cpp_info.libs = ["uchardet"]
        if self.options.shared:
            self.cpp_info.defines.append("UCHARDET_SHARED")

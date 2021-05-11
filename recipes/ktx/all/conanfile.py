from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibKtxConan(ConanFile):
    name = "libktx"
    description = "Khronos Texture library and tool"
    license = "Apache-2.0"
    topics = ("conan", "ktx")
    homepage = "https://github.com/KhronosGroup/KTX-Software"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
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

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "${CMAKE_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")
        tools.replace_in_file(cmakelists, "${CMAKE_BINARY_DIR}", "${CMAKE_CURRENT_BINARY_DIR}")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["KTX_FEATURE_STATIC_LIBRARY"] = \
            not self.options.shared
        self._cmake.definitions["KTX_FEATURE_TESTS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False

        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="licenses", src=os.path.join(self._source_subfolder, "LICENSES"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Ktx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Ktx"
        self.cpp_info.names["cmake_find_package"] = "KTX"
        self.cpp_info.names["cmake_find_package_multi"] = "KTX"
        self.cpp_info.components["ktx"].names["cmake_find_package"] = "ktx"
        self.cpp_info.components["ktx"].names["cmake_find_package_multi"] = "ktx"
        self.cpp_info.components["ktx"].libs = ["ktx"]
        self.cpp_info.components["ktx"].defines = [
            "KTX_FEATURE_KTX1", "KTX_FEATURE_KTX2", "KTX_FEATURE_WRITE"
        ]
        if self.settings.os == "Windows":
            self.cpp_info.components["ktx"].defines.append("BASISU_NO_ITERATOR_DEBUG_LEVEL")
        if not self.options.shared:
            self.cpp_info.components["ktx"].defines.append("KHRONOS_STATIC")
        if self.settings.os == "Linux":
            self.cpp_info.components["ktx"].system_libs = ["m", "dl", "pthread"]

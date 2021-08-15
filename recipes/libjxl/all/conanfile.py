from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class LibjxlConan(ConanFile):
    name = "libjxl"
    description = "JPEG XL image format reference implementation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libjxl/libjxl"
    topics = ("image", "jpeg-xl", "jxl", "jpeg")
    requires = "brotli/1.0.9", "highway/0.12.2", "lcms/2.11"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "CMakeLists.txt", "patches/**"
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "add_subdirectory(third_party)", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["JPEGXL_STATIC"] = not self.options.shared
        self._cmake.definitions["JPEGXL_ENABLE_BENCHMARK"] = False
        self._cmake.definitions["JPEGXL_ENABLE_EXAMPLES"] = False
        self._cmake.definitions["JPEGXL_ENABLE_SJPEG"] = False
        self._cmake.definitions["JPEGXL_ENABLE_OPENEXR"] = False
        self._cmake.definitions["JPEGXL_ENABLE_SKCMS"] = False
        self._cmake.definitions["JPEGXL_ENABLE_TCMALLOC"] = False
        if tools.cross_building(self):
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = \
                str(self.settings.arch)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            self.copy("libjxl_dec*", src="lib", dst="lib")
            tools.remove_files_by_mask(
                os.path.join(self.package_folder, "lib"), "*.a")

    def package_info(self):
        # jxl
        self.cpp_info.components["jxl"].names["pkg_config"] = "libjxl"
        self.cpp_info.components["jxl"].libs = ["jxl"]
        self.cpp_info.components["jxl"].requires = ["brotli::brotli",
                                                    "highway::highway",
                                                    "lcms::lcms"]
        # jxl_dec
        self.cpp_info.components["jxl_dec"].names["pkg_config"] = "libjxl_dec"
        self.cpp_info.components["jxl_dec"].libs = ["jxl_dec"]
        self.cpp_info.components["jxl_dec"].requires = ["brotli::brotli",
                                                        "highway::highway",
                                                        "lcms::lcms"]
        # jxl_threads
        self.cpp_info.components["jxl_threads"].names["pkg_config"] = \
            "libjxl_threads"
        self.cpp_info.components["jxl_threads"].libs = ["jxl_threads"]
        if self.settings.os == "Linux":
            self.cpp_info.components["jxl_threads"].system_libs = ["pthread"]

        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["jxl"].system_libs.append(
                tools.stdcpp_library(self))
            self.cpp_info.components["jxl_dec"].system_libs.append(
                tools.stdcpp_library(self))
            self.cpp_info.components["jxl_threads"].system_libs.append(
                tools.stdcpp_library(self))

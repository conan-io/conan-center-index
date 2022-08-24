from conan import ConanFile, tools
from conans import CMake
import os
import shutil
import glob

required_conan_version = ">=1.33.0"


class LibjxlConan(ConanFile):
    name = "libjxl"
    description = "JPEG XL image format reference implementation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libjxl/libjxl"
    topics = ("image", "jpeg-xl", "jxl", "jpeg")

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

    def requirements(self):
        self.requires("brotli/1.0.9")
        self.requires("highway/0.12.2")
        self.requires("lcms/2.11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["JPEGXL_STATIC"] = not self.options.shared
        self._cmake.definitions["JPEGXL_ENABLE_BENCHMARK"] = False
        self._cmake.definitions["JPEGXL_ENABLE_EXAMPLES"] = False
        self._cmake.definitions["JPEGXL_ENABLE_MANPAGES"] = False
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
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.shared:
            libs_dir = os.path.join(self.package_folder, "lib")
            tools.remove_files_by_mask(libs_dir, "*.a")
            tools.remove_files_by_mask(libs_dir, "*-static.lib")

            if self.settings.os == "Windows":
                self.copy("jxl_dec.dll", src="bin", dst="bin")
                self.copy("jxl_dec.lib", src="lib", dst="lib")
                for dll_path in glob.glob(os.path.join(libs_dir, "*.dll")):
                    shutil.move(dll_path, os.path.join(self.package_folder,
                                "bin", os.path.basename(dll_path)))
            else:
                self.copy("libjxl_dec.*", src="lib", dst="lib")

    def _lib_name(self, name):
        if not self.options.shared and self.settings.os == "Windows":
            return name + "-static"
        return name

    def package_info(self):
        # jxl
        self.cpp_info.components["jxl"].names["pkg_config"] = "libjxl"
        self.cpp_info.components["jxl"].libs = [self._lib_name("jxl")]
        self.cpp_info.components["jxl"].requires = ["brotli::brotli",
                                                    "highway::highway",
                                                    "lcms::lcms"]
        # jxl_dec
        self.cpp_info.components["jxl_dec"].names["pkg_config"] = "libjxl_dec"
        self.cpp_info.components["jxl_dec"].libs = [self._lib_name("jxl_dec")]
        self.cpp_info.components["jxl_dec"].requires = ["brotli::brotli",
                                                        "highway::highway",
                                                        "lcms::lcms"]
        # jxl_threads
        self.cpp_info.components["jxl_threads"].names["pkg_config"] = \
            "libjxl_threads"
        self.cpp_info.components["jxl_threads"].libs = \
            [self._lib_name("jxl_threads")]
        if self.settings.os == "Linux":
            self.cpp_info.components["jxl_threads"].system_libs = ["pthread"]

        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["jxl"].system_libs.append(
                tools.stdcpp_library(self))
            self.cpp_info.components["jxl_dec"].system_libs.append(
                tools.stdcpp_library(self))
            self.cpp_info.components["jxl_threads"].system_libs.append(
                tools.stdcpp_library(self))

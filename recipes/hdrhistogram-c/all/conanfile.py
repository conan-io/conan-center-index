from conans import ConanFile, CMake, tools
import os


class HdrhistogramcConan(ConanFile):
    name = "hdrhistogram-c"
    license = ("BSD-2-Clause", "CC0-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HdrHistogram/HdrHistogram_c"
    description = "'C' port of High Dynamic Range (HDR) Histogram"
    topics = ("libraries", "c", "histogram")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("HdrHistogram_c-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["HDR_HISTOGRAM_BUILD_PROGRAMS"] = False
            self._cmake.definitions["HDR_HISTOGRAM_BUILD_SHARED"] = self.options.shared
            self._cmake.definitions["HDR_HISTOGRAM_INSTALL_SHARED"] = self.options.shared
            self._cmake.definitions["HDR_HISTOGRAM_BUILD_STATIC"] = not self.options.shared
            self._cmake.definitions["HDR_HISTOGRAM_INSTALL_STATIC"] = not self.options.shared
            self._cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
            self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "hdr_histogram"
        self.cpp_info.names["cmake_find_package_multi"] = "hdr_histogram"
        hdr_histogram_target = "hdr_histogram" if self.options.shared else "hdr_histogram_static"
        self.cpp_info.components["hdr_histrogram"].names["cmake_find_package"] = hdr_histogram_target
        self.cpp_info.components["hdr_histrogram"].names["cmake_find_package_multi"] = hdr_histogram_target
        self.cpp_info.components["hdr_histrogram"].libs = tools.collect_libs(self)
        self.cpp_info.components["hdr_histrogram"].includedirs = ["include", os.path.join("include", "hdr")]
        self.cpp_info.components["hdr_histrogram"].requires = ["zlib::zlib"]
        if self.settings.os == "Linux":
            self.cpp_info.components["hdr_histrogram"].system_libs = ["m", "rt"]
        elif self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.components["hdr_histrogram"].system_libs = ["ws2_32"]

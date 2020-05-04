import glob
import os

from conans import ConanFile, CMake, tools

class ProjConan(ConanFile):
    name = "proj"
    description = "Cartographic Projections and Coordinate Transformations Library."
    license = "MIT"
    topics = ("conan", "dsp", "proj", "proj4", "projections", "gis", "geospatial")
    homepage = "https://proj.org"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "with_tiff": [True, False],
        "with_curl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True,
        "with_tiff": True,
        "with_curl": True
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

    def requirements(self):
        self.requires.add("sqlite3/3.31.1")
        if self.options.with_tiff:
            self.requires.add("libtiff/4.1.0")
        if self.options.with_curl:
            self.requires.add("libcurl/7.69.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_TIFF"] = self.options.with_tiff
        self._cmake.definitions["ENABLE_CURL"] = self.options.with_curl
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["USE_THREAD"] = self.options.threadsafe
        self._cmake.definitions["ENABLE_IPO"] = False
        self._cmake.definitions["BUILD_CCT"] = True
        self._cmake.definitions["BUILD_CS2CS"] = True
        self._cmake.definitions["BUILD_GEOD"] = True
        self._cmake.definitions["BUILD_GIE"] = True
        self._cmake.definitions["BUILD_PROJ"] = True
        self._cmake.definitions["BUILD_PROJINFO"] = True
        self._cmake.definitions["BUILD_PROJSYNC"] = True
        self._cmake.definitions["PROJ_DATA_SUBDIR"] = "res"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        for data_file in glob.glob(os.path.join(self.package_folder, "res", "*")):
            if not data_file.endswith("proj.db"):
                os.remove(data_file)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PROJ"
        self.cpp_info.names["cmake_find_package_multi"] = "PROJ"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
        if not self.options.shared and self._stdcpp_library:
            self.cpp_info.system_libs.append(self._stdcpp_library)
        if self.options.shared and self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("PROJ_MSVC_DLL_IMPORT")
        self.env_info.PROJ_LIB.append(os.path.join(self.package_folder, "res"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    @property
    def _stdcpp_library(self):
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx in ("libstdc++", "libstdc++11"):
            return "stdc++"
        elif libcxx in ("libc++",):
            return "c++"
        else:
            return False

from conans import ConanFile, CMake, tools
import glob
import os


class ProjConan(ConanFile):
    name = "proj"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://proj.org"
    description = "Cartographic Projections and Coordinate Transformations Library"
    topics = ("conan", "dsp", "proj", "proj4", "projections", "gis", "geospatial")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True
    }

    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PROJ_TESTS"] = False
        self._cmake.definitions["BUILD_LIBPROJ_SHARED"] = self.options.shared
        self._cmake.definitions["USE_THREAD"] = self.options.threadsafe
        self._cmake.definitions["ENABLE_LTO"] = False
        self._cmake.definitions["JNI_SUPPORT"] = False
        self._cmake.definitions["BUILD_CCT"] = True
        self._cmake.definitions["BUILD_CS2CS"] = True
        self._cmake.definitions["BUILD_GEOD"] = True
        self._cmake.definitions["BUILD_GIE"] = True
        self._cmake.definitions["BUILD_PROJ"] = True
        self._cmake.definitions["BUILD_PROJINFO"] = True
        self._cmake.definitions["PROJ_DATA_SUBDIR"] = "res"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        for data_file in glob.glob(os.path.join(self.package_folder, "res", "*")):
            if not data_file.endswith("proj.db"):
                os.remove(data_file)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PROJ4"
        self.cpp_info.names["cmake_find_package_multi"] = "PROJ4"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
        if self.options.shared and self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("PROJ_MSVC_DLL_IMPORT")
        self.env_info.PROJ_LIB.append(os.path.join(self.package_folder, "res"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

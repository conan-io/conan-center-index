from conans import ConanFile, CMake, tools
import os


class LibaecConan(ConanFile):
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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "sqlite_init.py", "patches/*"]

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
        self.requires("sqlite3/3.31.0")

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
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "lib_proj.cmake"),
                              "include_directories(${CMAKE_SOURCE_DIR}/include)",
                              "include_directories(${PROJ4_SOURCE_DIR}/include)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*.db",
                  src=os.path.join(self.package_folder, "share", "proj"),
                  dst=os.path.join(self.package_folder, "lib", "proj"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
        self.env_info.PROJ_LIB.append(os.path.join(self.package_folder, "lib", "proj"))

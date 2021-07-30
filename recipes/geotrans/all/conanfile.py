from conans import ConanFile, CMake, tools
import os
import shutil


class GeotransConan(ConanFile):
    name = "geotrans"
    version = "3.8"
    license = (
        "NGA GEOTRANS ToS (https://earth-info.nga.mil/php/download.php?file=wgs-terms)"
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://earth-info.nga.mil/"
    description = "MSP GEOTRANS is the NGA and DOD approved coordinate converter and datum translator."
    topics = (
        "geotrans",
        "geodesic",
        "geographic",
        "coordinate",
        "datum",
        "geodetic",
        "conversion",
        "transformation",
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder,
            filename="master.tgz"
        )
        shutil.copy("CMakeLists.txt", self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(
            "*.txt",
            dst="licenses",
            src=os.path.join(self._source_subfolder, "GEOTRANS3", "docs"),
        )
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.user_info.data_path = os.path.join(self.package_folder, "res")
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.names["cmake_find_package"] = "geotrans"
        self.cpp_info.names["cmake_find_package_multi"] = "geotrans"
        self.cpp_info.components["dtcc"].names["cmake_find_package"] = "dtcc"
        self.cpp_info.components["dtcc"].names["cmake_find_package_multi"] = "dtcc"
        self.cpp_info.components["dtcc"].libs = ["MSPdtcc"]
        self.cpp_info.components["dtcc"].includedirs = [
            path[0]
            for path in os.walk(os.path.join("include", "dtcc", "CoordinateSystems"))
        ]
        self.cpp_info.components["dtcc"].system_libs = ["pthread"]
        self.cpp_info.components["ccs"].names["cmake_find_package"] = "ccs"
        self.cpp_info.components["ccs"].names["cmake_find_package_multi"] = "ccs"
        self.cpp_info.components["ccs"].libs = ["MSPCoordinateConversionService"]
        self.cpp_info.components["ccs"].requires = ["dtcc"]
        self.cpp_info.components["ccs"].includedirs = [
            path[0] for path in os.walk("include")
        ]
        self.cpp_info.components["ccs"].system_libs = ["pthread"]

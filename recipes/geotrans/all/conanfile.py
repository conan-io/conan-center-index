from conans import ConanFile, CMake, tools
import os


class GeotransConan(ConanFile):
    name = "geotrans"
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
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder,
            filename="master.tgz"
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
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
        mpccs_data_path = os.path.join(self.package_folder, "res")
        self.output.info("Creating MPCCS_DATA environment variable: {}".format(mpccs_data_path))
        self.env_info.MPCCS_DATA = mpccs_data_path
        self.cpp_info.components["dtcc"].libs = ["MSPdtcc"]
        self.cpp_info.components["dtcc"].includedirs = [
            path[0] for path in os.walk("include")
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["dtcc"].system_libs.append("pthread")

        self.cpp_info.components["ccs"].libs = ["MSPCoordinateConversionService"]
        self.cpp_info.components["ccs"].requires = ["dtcc"]
        self.cpp_info.components["ccs"].includedirs = [
            path[0] for path in os.walk("include")
        ]

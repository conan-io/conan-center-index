from conans import ConanFile, CMake, tools
import os
import shutil


class GeotransConan(ConanFile):
    name = "geotrans"
    version = "3.8"
    license = (
        "NGA GEOTRANS ToS (https://earth-info.nga.mil/php/download.php?file=wgs-terms)"
    )
    url = "https://earth-info.nga.mil/"
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
    default_options = {"shared": True, "fPIC": True}
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
        self._cmake.configure(
            source_folder=self._source_subfolder
        )
        return self._cmake


    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*.txt", dst="licenses", src=os.path.join(self._source_subfolder, "GEOTRANS3", "docs"))
        self.copy("*", dst="res", src=os.path.join(self._source_subfolder, "data"))
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "CCS", "src"))
        self.copy("*.lib", dst="lib", src="lib", keep_path=False)
        self.copy("*.dll", dst="bin", src="lib", keep_path=False)
        self.copy("*.so", dst="lib", src="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", src="lib", keep_path=False)
        self.copy("*.a", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.cxxflags = ["-pthread"]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [path[0] for path in os.walk("include")]

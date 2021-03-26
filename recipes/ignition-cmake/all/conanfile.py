import glob
import os

from conans import CMake, ConanFile, tools


class IgnitionCmakeConan(ConanFile):
    name = "ignition-cmake"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ignitionrobotics/ign-cmake"
    description = "A set of CMake modules that are used by the C++-based Ignition projects."
    topics = ("ignition", "robotics", "cmake")
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_INSTALL_DATAROOTDIR"] = "lib"
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("ign-cmake*")[0], self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        version_major = tools.Version(self.version).major
        self.cpp_info.names["cmake_find_package"] = "ignition-cmake{}".format(version_major)
        self.cpp_info.names["cmake_find_package_multi"] = "ignition-cmake{}".format(version_major)
        self.cpp_info.builddirs = [
            os.path.join("lib", "cmake", "ignition-cmake{}".format(version_major)),
            os.path.join("lib", "cmake", "ignition-cmake{}".format(version_major), "cmake{}".format(version_major)),
        ]

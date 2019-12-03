import os
import stat
from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
from conans.errors import ConanException

class apriltagConan(ConanFile):
    name = "apriltag"
    license = "BSD-2-Clause"
    homepage = "https://april.eecs.umich.edu/software/apriltag"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("AprilTag is a visual fiducial system, useful for a wide variety of tasks \
                    including augmented reality, robotics, and camera calibration")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    generators = "cmake"
    topics = ("conan", "apriltag", "robotics")
    exports_sources = ["CMakeLists.txt", "*.patch"]
    _source_subfolder = "source_subfolder"
    _cmake = None

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure()
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
        self.cpp_info.includedirs = ["include",os.path.join("include","apriltag")]

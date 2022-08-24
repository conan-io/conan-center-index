from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration
import os


class ApriltagConan(ConanFile):
    name = "apriltag"
    description = ("AprilTag is a visual fiducial system, useful for a wide variety of tasks \
                    including augmented reality, robotics, and camera calibration")
    homepage = "https://april.eecs.umich.edu/software/apriltag"
    topics = ("conan", "apriltag", "robotics")
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Apriltag officially supported only on Linux")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
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
        self.cpp_info.names["cmake_find_package"] = "apriltag"
        self.cpp_info.names["cmake_find_package_multi"] = "apriltag"

        self.cpp_info.libs = ["apriltag"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
        self.cpp_info.includedirs.append(os.path.join("include","apriltag"))

import os

from conans import CMake, ConanFile, tools


class SDFormat(ConanFile):
    name = "sdformat"
    license = "Apache-2.0"
    homepage = "http://sdformat.org/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Simulation Description Format (SDFormat) parser and description files."
    topics = ("ignition", "robotics", "simulation")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        version_major = self.version.split('.')[0]
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(f"sdformat-sdformat{version_major}_{self.version}", self._source_subfolder)

    def requirements(self):
        self.requires("ignition-math/6.4.0")
        self.requires("tinyxml2/8.0.0")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["USE_INTERNAL_URDF"] = True
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        version_major = self.version.split('.')[0]
        version_till_minor = ".".join(self.version.split(".")[0:2])
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = f"sdformat{version_major}"
        self.cpp_info.names["cmake_find_package_multi"] = f"sdformat{version_major}"
        self.cpp_info.includedirs = [f"include/sdformat-{version_till_minor}"]

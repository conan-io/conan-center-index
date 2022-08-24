import os
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.29.1"


class Box2dConan(ConanFile):
    name = "box2d"
    license = "Zlib"
    description = "Box2D is a 2D physics engine for games"
    homepage = "http://box2d.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("physics-engine", "graphic", "2d", "collision")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True,}

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
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
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("box2d-%s" % self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BOX2D_BUILD_TESTBED"] = False
        self._cmake.definitions["BOX2D_BUILD_UNIT_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "box2d"
        self.cpp_info.names["cmake_find_package_multi"] = "box2d"
        self.cpp_info.libs = ["box2d"]
        if tools.Version(self.version) >= "2.4.1" and self.options.shared:
            self.cpp_info.defines.append("B2_SHARED")

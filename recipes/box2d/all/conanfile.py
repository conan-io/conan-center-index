import os
from conans import ConanFile, CMake, tools


class Box2dConan(ConanFile):
    name = "box2d"
    license = "Zlib"
    description = "Box2D is a 2D physics engine for games"
    topics = ("physics", "engine", "game development")
    homepage = "http://box2d.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True,}
    generators = "cmake"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "sources"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("box2d-%s" % self.version, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BOX2D_BUILD_SHARED"] = self.options.shared
        cmake.definitions["BOX2D_BUILD_STATIC"] = not self.options.shared
        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        cmake.definitions["BOX2D_BUILD_EXAMPLES"] = False
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("License.txt", dst="licenses", src=os.path.join(self._source_subfolder, "Box2D"))
        self.copy("*.h", dst=os.path.join("include", "Box2D"), src=os.path.join(self._source_subfolder, "Box2D", "Box2D"))
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Box2D"]

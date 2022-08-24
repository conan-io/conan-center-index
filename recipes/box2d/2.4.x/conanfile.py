import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.scm import Version

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
    exports_sources = ["patches/**"]

    def config_options(self):
        if self.settings.os == "Windows":
            try:
                del self.options.fPIC
            except Exception:
                pass

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BOX2D_BUILD_TESTBED"] = False
        tc.variables["BOX2D_BUILD_UNIT_TESTS"] = False
        tc.generate()

    def build(self):
        tools.files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses")
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "box2d"
        self.cpp_info.names["cmake_find_package_multi"] = "box2d"
        self.cpp_info.libs = ["box2d"]
        if Version(self.version) >= "2.4.1" and self.options.shared:
            self.cpp_info.defines.append("B2_SHARED")

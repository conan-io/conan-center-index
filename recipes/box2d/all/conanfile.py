import os
from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout

required_conan_version = ">=1.46.0"


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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self,
                        **self.conan_data["sources"][self.version],
                        strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BOX2D_BUILD_SHARED"] = self.options.shared
        tc.variables["BOX2D_BUILD_STATIC"] = not self.options.shared
        if self.settings.os == "Windows" and self.options.shared:
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["BOX2D_BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="Box2D")
        cmake.build()

    def package(self):
        tools.files.copy(self, "License.txt", src=os.path.join(self.source_folder, "Box2D"), dst=os.path.join(self.package_folder,"licenses"))
        tools.files.copy(self, os.path.join("Box2D", "*.h"), src=os.path.join(self.source_folder, "Box2D"), dst=os.path.join(self.package_folder, "include"))
        tools.files.copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        tools.files.copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        tools.files.copy(self, "*.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        tools.files.copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        tools.files.copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        print(self.cpp_info.includedirs)
        self.cpp_info.libs = ["Box2D"]


    def layout(self):
        cmake_layout(self, src_folder="Box2D")

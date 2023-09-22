from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, export_conandata_patches
import os

class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot script API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("game-engine", "game-development", "c++")
    package_type = "static-library"
    settings = ("arch", "build_type", "compiler", "os")
    generators = ["CMakeToolchain"]

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        platform = {
            "Android": "android",
            "Linux": "linux",
            "Macos": "darwin",
            "Windows": "windows",
        }[str(self.settings.os)]
        build_type = str(self.settings.build_type).lower()

        if self.settings.os == "Android":
            self.cpp_info.libs= [f"godot-cpp.{platform}.{build_type}"]
        else:
            bits = 64 if self.settings.arch in ["x86_64", "armv8"] else 32
            self.cpp_info.libs= [f"godot-cpp.{platform}.{build_type}.{bits}"]

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, "17")

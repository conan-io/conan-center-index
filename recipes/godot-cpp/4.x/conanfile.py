import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.android import android_abi
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0"


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot script API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("game-engine", "game-development", "c++")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self._system is None:
            raise ConanInvalidConfiguration(f"Unsupported system: {self.settings.os}")
        if self._arch is None:
            raise ConanInvalidConfiguration(f"Unsupported architecture: {self.settings.arch}")
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cpython/[~3.12]")

    @property
    def _system(self):
        # https://github.com/godotengine/godot-cpp/blob/godot-4.4-stable/cmake/godotcpp.cmake#L260-L268
        if self.settings.os == "Android":
            return f"android.{android_abi(self)}"
        return {
            "Windows": "windows",
            "Linux": "linux",
            "Macos": "osx",
            "iOS": "ios",
            "Emscripten": "web",
        }.get(str(self.settings.os))

    @property
    def _target(self):
        return "template_debug" if self.settings.build_type == "Debug" else "template_release"

    @property
    def _arch(self):
        # https://github.com/godotengine/godot-cpp/blob/godot-4.4-stable/cmake/godotcpp.cmake#L47-L99
        return {
            "x86": "x86",
            "x86_64": "x86_64",
            "armv7": "arm32",
            "armv8": "arm64",
            "riscv64": "rv64",
            "ppc": "ppc32",
            "ppc64le": "ppc64",
        }.get(str(self.settings.arch))

    @property
    def _libname(self):
        return f"godot-cpp.{self._system}.{self._target}.{self._arch}"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GODOTCPP_ENABLE_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=f"godot-cpp.{self._target}")

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "gdextension_interface.h",
             os.path.join(self.source_folder, "gdextension"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp",
             os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp",
             os.path.join(self.build_folder, "gen", "include"),
             os.path.join(self.package_folder, "include"))
        bin_dir = os.path.join(self.build_folder, "bin")
        copy(self, "*.a", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.lib", bin_dir, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        # https://github.com/godotengine/godot-cpp/blob/godot-4.4-stable/cmake/godotcpp.cmake#L311
        self.cpp_info.set_property("cmake_target_aliases", [f"godot-cpp::{self._target}"])

        if is_msvc(self):
            self.cpp_info.libs = [f"lib{self._libname}"]
        else:
            self.cpp_info.libs = [self._libname]

import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0.9"


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot script API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("game-engine", "game-development", "c++")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"godot_headers/{self.version}", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("cpython/[~3.12]")

    @property
    def _godot_headers(self):
        return self.dependencies["godot_headers"].cpp_info

    @property
    def _custom_api_file(self):
        return f"{self._godot_headers.resdirs[0]}/api.json"

    @property
    def _headers_dir(self):
        return self._godot_headers.includedir

    @property
    def _platform(self):
        flag_map = {
            "Windows": "windows",
            "Linux": "linux",
            "Macos": "osx",
        }
        return flag_map[str(self.settings.os)]

    @property
    def _target(self):
        return "debug" if self.settings.build_type == "Debug" else "release"

    @property
    def _bits(self):
        return 32 if self.settings.arch in ["x86"] else 64

    @property
    def _libname(self):
        return f"godot-cpp.{self._platform}.{self._target}.{self._bits}"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GODOT_HEADERS_DIR"] = self._headers_dir.replace("\\", "/")
        tc.variables["GODOT_CUSTOM_API_FILE"] = self._custom_api_file.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include/godot-cpp"))
        bin_dir = os.path.join(self.source_folder, "bin")
        copy(self, "*.a", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.so", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.lib", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.dll", bin_dir, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if is_msvc(self):
            self.cpp_info.libs = [f"lib{self._libname}"]
        else:
            self.cpp_info.libs = [self._libname]

        self.cpp_info.includedirs = [
            os.path.join("include", "godot-cpp"),
            os.path.join("include", "godot-cpp", "core"),
            os.path.join("include", "godot-cpp", "gen"),
        ]

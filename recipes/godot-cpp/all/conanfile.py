import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot script API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("game-engine", "game-development", "c++")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"godot_headers/{self.version}", transitive_headers=True)

    def package_id(self):
        if self.info.settings.build_type != "Debug":
            self.info.settings.build_type = "Release"

    def validate(self):
        minimal_cpp_standard = 14
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {compiler} compiler standard version support"
            )
            self.output.warning(
                f"{self.name} requires a compiler that supports at least C++{minimal_cpp_standard}"
            )
            return

        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            if compiler in ["apple-clang", "clang"]:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires a clang version that supports the '-Og' flag"
                )
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++{minimal_cpp_standard}"
            )

    def build_requirements(self):
        self.tool_requires("scons/4.3.0")

    @property
    def _bits(self):
        return 32 if self.settings.arch in ["x86"] else 64

    @property
    def _godot_headers(self):
        return self.dependencies["godot_headers"].cpp_info

    @property
    def _custom_api_file(self):
        return f"{self._godot_headers.resdirs[0]}/api.json"

    @property
    def _headers_dir(self):
        return self._godot_headers.includedirs[0]

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
    def _use_llvm(self):
        return self.settings.compiler in ["clang", "apple-clang"]

    @property
    def _use_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _libname(self):
        return f"godot-cpp.{self._platform}.{self._target}.{self._bits}"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

    def build(self):
        self.run("python  --version")
        if is_apple_os(self):
            self.run("which python")
        self.run("scons  --version")
        self.run(" ".join([
            "scons",
            f"-C{self.source_folder}",
            f"-j{os.cpu_count()}",
            "generate_bindings=yes",
            "use_custom_api_file=yes",
            f"bits={self._bits}",
            f"custom_api_file={self._custom_api_file}",
            f"headers_dir={self._headers_dir}",
            f"platform={self._platform}",
            f"target={self._target}",
            f"use_llvm={self._use_llvm}",
            f"use_mingw={self._use_mingw}",
        ]))

    def package(self):
        copy(self, "LICENSE*",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.hpp",
             dst=os.path.join(self.package_folder, "include/godot-cpp"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "*.a",
             dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, "bin"))
        copy(self, "*.lib",
             dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, "bin"))

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

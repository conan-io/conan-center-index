import glob
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rename
from conan.tools.scm import Version


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot script API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("game-engine", "game-development", "c++")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    build_requires = ["scons/3.1.2"]

    @property
    def _bits(self):
        return 64 if self.settings.get_safe("arch") in ["x86_64", "armv8"] else 32

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
        return flag_map[self.settings.get_safe("os")]

    @property
    def _target(self):
        return "debug" if self.settings.get_safe("build_type") == "Debug" else "release"

    @property
    def _use_llvm(self):
        return self.settings.get_safe("compiler") in ["clang", "apple-clang"]

    @property
    def _use_mingw(self):
        return self._platform == "windows" and self.settings.compiler == "gcc"

    @property
    def _libname(self):
        return f"godot-cpp.{self._platform}.{self._target}.{self._bits}"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _godot_headers(self):
        return self.dependencies["godot_headers"].cpp_info

    def _destination_dir(self, path):
        return os.path.join(self.package_folder, path)

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        rename(self, glob.glob("godot-cpp-*")[0], self._source_subfolder)

    def requirements(self):
        self.requires(f"godot_headers/{self.version}", transitive_headers=True)

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "10",
            "Visual Studio": "15",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                f"{self.name} recipe lacks information about the {compiler} compiler standard version support")
            self.output.warn(
                f"{self.name} requires a compiler that supports at least C++{minimal_cpp_standard}")
            return

        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            if compiler in ["apple-clang", "clang"]:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires a clang version that supports the '-Og' flag")
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++{minimal_cpp_standard}")

    def build(self):
        self.run("python  --version")
        if self.settings.os == "Macos":
            self.run("which python")
        self.run("scons  --version")
        self.run(
            " ".join([
                "scons",
                f"-C{self._source_subfolder}",
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
            ])
        )

    def package(self):
        copy(self, "LICENSE*", dst=self._destination_dir("licenses"), src=self._source_subfolder)
        copy(self, "*.hpp", dst=self._destination_dir("include/godot-cpp"), src=os.path.join(self._source_subfolder, "include"))
        copy(self, "*.a", dst=self._destination_dir("lib"), src=os.path.join(self._source_subfolder, "bin"))
        copy(self, "*.lib", dst=self._destination_dir("lib"), src=os.path.join(self._source_subfolder, "bin"))

    def package_info(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = [f"lib{self._libname}"]
        else:
            self.cpp_info.libs = [self._libname]

        self.cpp_info.includedirs = [
            os.path.join("include", "godot-cpp"),
            os.path.join("include", "godot-cpp", "core"),
            os.path.join("include", "godot-cpp", "gen"),
        ]

    def package_id(self):
        if self.info.settings.build_type != "Debug":
            self.info.settings.build_type = "Release"

import glob
import os

from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot script API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("game-engine", "game-development", "c++")
    settings = "os", "arch", "compiler", "build_type"
    build_requires = ["scons/3.1.2"]

    @property
    def _bits(self):
        return 64 if self.settings.get_safe("arch") in ["x86_64", "armv8"] else 32

    @property
    def _custom_api_file(self):
        return "{}/api.json".format(self._godot_headers.res_paths[0])

    @property
    def _headers_dir(self):
        return self._godot_headers.include_paths[0]

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
        return "godot-cpp.{platform}.{target}.{bits}".format(platform=self._platform, target=self._target, bits=self._bits)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _godot_headers(self):
        return self.deps_cpp_info["godot_headers"]

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        tools.files.rename(self, glob.glob("godot-cpp-*")[0], self._source_subfolder)

    def requirements(self):
        self.requires("godot_headers/{}".format(self.version))

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "10",
            "Visual Studio": "15",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
            self.output.warn(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            if compiler in ["apple-clang", "clang"]:
                raise ConanInvalidConfiguration(
                    "{} requires a clang version that supports the '-Og' flag".format(self.name))
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))

    def build(self):
        self.run("python  --version")
        if self.settings.os == "Macos":
            self.run("which python")
        self.run("scons  --version")
        self.run(
            " ".join([
                "scons",
                "-C{}".format(self._source_subfolder),
                "-j{}".format(tools.cpu_count(self, )),
                "generate_bindings=yes",
                "use_custom_api_file=yes",
                "bits={}".format(self._bits),
                "custom_api_file={}".format(self._custom_api_file),
                "headers_dir={}".format(self._headers_dir),
                "platform={}".format(self._platform),
                "target={}".format(self._target),
                "use_llvm={}".format(self._use_llvm),
                "use_mingw={}".format(self._use_mingw),
            ])
        )

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include/godot-cpp", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.a", dst="lib", src=os.path.join(self._source_subfolder, "bin"))
        self.copy("*.lib", dst="lib", src=os.path.join(self._source_subfolder, "bin"))

    def package_info(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["lib{}".format(self._libname)]
        else:
            self.cpp_info.libs = [self._libname]

        self.cpp_info.includedirs = [
            os.path.join("include", "godot-cpp"),
            os.path.join("include", "godot-cpp", "core"),
            os.path.join("include", "godot-cpp", "gen"),
        ]

    def package_id(self):
        if self._target == "release":
            self.info.settings.build_type = "Release"
        else:
            self.info.settings.build_type = "Debug"

from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"

class MiniaudioConan(ConanFile):
    name = "miniaudio"
    description = "A single file audio playback and capture library."
    license = ["Unlicense", "MIT-0"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mackron/miniaudio"
    topics = ("audio", "header-only", "sound")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only or self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.header_only:
            del self.options.shared
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.header_only:
            return

        tc = CMakeToolchain(self)
        tc.variables["MINIAUDIO_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["MINIAUDIO_VERSION_STRING"] = self.version
        tc.generate()

    def build(self):
        if self.options.header_only:
            return

        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="**",
            dst=os.path.join(self.package_folder, "include", "extras"),
            src=os.path.join(self.source_folder, "extras"),
        )

        if self.options.header_only:
            copy(
                self,
                pattern="miniaudio.h",
                dst=os.path.join(self.package_folder, "include"),
                src=self.source_folder)
            copy(
                self,
                pattern="miniaudio.*",
                dst=os.path.join(self.package_folder, "include", "extras", "miniaudio_split"),
                src=os.path.join(self.source_folder, "extras", "miniaudio_split"),
            )
        else:
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(
                ["CoreFoundation", "CoreAudio", "AudioUnit"]
            )
            self.cpp_info.defines.append("MA_NO_RUNTIME_LINKING=1")

        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs = ["miniaudio"]
            if self.options.shared:
                self.cpp_info.defines.append("MA_DLL")

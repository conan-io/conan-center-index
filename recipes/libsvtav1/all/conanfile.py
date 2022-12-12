import os
from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.47.0"


class SVTAV1Conan(ConanFile):
    name = "libsvtav1"
    license = "BSD-3-Clause"
    description = "An AV1-compliant software encoder/decoder library"
    topics = "encoder", "ffmpeg", "av1"
    homepage = "https://gitlab.com/AOMediaCodec/SVT-AV1"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "build_encoder": [True, False],
        "build_decoder": [True, False],
    }
    default_options = {
        "fPIC": False,
        "build_encoder": True,
        "build_decoder": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("nasm/2.15.05")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_APPS"] = False
        tc.variables["BUILD_DEC"] = self.options.build_decoder
        tc.variables["BUILD_ENC"] = self.options.build_encoder
        if self.settings.arch in ("x86", "x86_64"):
            tc.variables["ENABLE_NASM"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE.md",
            self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "PATENTS.md",
            self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
        if self.options.build_encoder:
            self.cpp_info.components["encoder"].libs = ["SvtAv1Enc"]
            self.cpp_info.components["encoder"].includedirs = ["include/svt-av1"]
            self.cpp_info.components["encoder"].set_property("pkg_config_name", "SvtAv1Enc")
            self.cpp_info.components["encoder"].names["pkg_config"] = "SvtAv1Enc"
        if self.options.build_decoder:
            self.cpp_info.components["decoder"].libs = ["SvtAv1Dec"]
            self.cpp_info.components["decoder"].includedirs = ["include/svt-av1"]
            self.cpp_info.components["decoder"].set_property("pkg_config_name", "SvtAv1Dec")
            self.cpp_info.components["decoder"].names["pkg_config"] = "SvtAv1Dec"

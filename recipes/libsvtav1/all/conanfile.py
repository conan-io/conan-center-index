import os
from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SVTAV1Conan(ConanFile):
    name = "libsvtav1"
    license = "BSD-3-Clause"
    description = "An AV1-compliant software encoder/decoder library"
    topics = "av1", "codec", "encoder", "decoder", "video"
    homepage = "https://gitlab.com/AOMediaCodec/SVT-AV1"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_encoder": [True, False],
        "build_decoder": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_encoder": True,
        "build_decoder": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpuinfo/cci.20231129")

    def build_requirements(self):
        if Version(self.version) >= "1.3.0":
            self.tool_requires("cmake/[>=3.16 <4]")
        if self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("nasm/2.15.05")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_APPS"] = False
        tc.variables["BUILD_DEC"] = self.options.build_decoder
        tc.variables["BUILD_ENC"] = self.options.build_encoder
        tc.variables["USE_EXTERNAL_CPUINFO"] = True
        if self.settings.arch in ("x86", "x86_64"):
            tc.variables["ENABLE_NASM"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE.md", "PATENTS.md"):
            copy(self, license_file, self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.options.build_encoder:
            self.cpp_info.components["encoder"].libs = ["SvtAv1Enc"]
            self.cpp_info.components["encoder"].includedirs = ["include/svt-av1"]
            self.cpp_info.components["encoder"].set_property("pkg_config_name", "SvtAv1Enc")
            self.cpp_info.components["encoder"].requires = ["cpuinfo::cpuinfo"]
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.components["encoder"].system_libs = ["pthread", "dl", "m"]
        if self.options.build_decoder:
            self.cpp_info.components["decoder"].libs = ["SvtAv1Dec"]
            self.cpp_info.components["decoder"].includedirs = ["include/svt-av1"]
            self.cpp_info.components["decoder"].set_property("pkg_config_name", "SvtAv1Dec")
            self.cpp_info.components["decoder"].requires = ["cpuinfo::cpuinfo"]
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.components["encoder"].system_libs = ["pthread", "dl", "m"]

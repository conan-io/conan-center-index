import os
from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.54.0"


class SVTAV1Conan(ConanFile):
    name = "libsvtav1"
    description = "An AV1-compliant software encoder/decoder library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/AOMediaCodec/SVT-AV1"
    topics = ("av1", "codec", "encoder", "decoder", "video")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_encoder": [True, False],
        "build_decoder": [True, False],
        "minimal_build": [True, False],
        "with_neon": [True, False],
        "with_arm_crc32": [True, False],
        "with_neon_dotprod": [True, False],
        "with_neon_i8mm": [True, False],
        "with_neon_sve": [True, False],
        "with_neon_sve2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_encoder": True,
        "build_decoder": True,
        "minimal_build": False,
        "with_neon": True,
        "with_arm_crc32": True,
        "with_neon_dotprod": True,
        "with_neon_i8mm": True,
        "with_neon_sve": True,
        "with_neon_sve2": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if Version(self.version) < "2.0.0":
            del self.options.minimal_build
        if Version(self.version) >= "2.1.1":
            # https://gitlab.com/AOMediaCodec/SVT-AV1/-/blob/c949fe4f14fe288a9b2b47aa3e61335422a83645/CHANGELOG.md#211---2024-06-25
            del self.options.build_decoder
        if Version(self.version) < "2.2.1" or self.settings.arch not in ("armv8", "armv8.3"):
            del self.options.with_neon
            del self.options.with_arm_crc32
            del self.options.with_neon_dotprod
            del self.options.with_neon_i8mm
            del self.options.with_neon_sve
            del self.options.with_neon_sve2

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpuinfo/cci.20231129")

    def validate(self):
        # https://gitlab.com/AOMediaCodec/SVT-AV1/-/issues/2081
        # https://gitlab.com/AOMediaCodec/SVT-AV1/-/commit/800a81b09db1cf8c9c289ecf6f70381d7888b98c
        if Version(self.version) < "1.9.0" and self.settings.os == "Android":
            raise ConanInvalidConfiguration(f"{self.ref} does not support Android before version 1.9.0.")

    def build_requirements(self):
        if Version(self.version) >= "1.3.0":
            self.tool_requires("cmake/[>=3.16 <4]")
        if self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("nasm/2.16.01")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_APPS"] = False
        if Version(self.version) < "2.1.1":
            tc.variables["BUILD_DEC"] = self.options.build_decoder
        tc.variables["BUILD_ENC"] = self.options.build_encoder
        tc.variables["USE_EXTERNAL_CPUINFO"] = True
        if self.settings.arch in ("x86", "x86_64"):
            tc.variables["ENABLE_NASM"] = True
        tc.variables["MINIMAL_BUILD"] = self.options.get_safe("minimal_build", False)
        if "with_neon" in self.options:
            tc.variables["ENABLE_NEON"] = self.options.with_neon
        if "with_arm_crc32" in self.options:
            tc.variables["ENABLE_ARM_CRC32"] = self.options.with_arm_crc32
        if "with_neon_dotprod" in self.options:
            tc.variables["ENABLE_NEON_DOTPROD"] = self.options.with_neon_dotprod
        if "with_neon_i8mm" in self.options:
            tc.variables["ENABLE_NEON_i8MM"] = self.options.with_neon_i8mm
        if "with_sve" in self.options:
            tc.variables["ENABLE_SVE"] = self.options.with_sve
        if "with_sve2" in self.options:
            tc.variables["ENABLE_SVE2"] = self.options.with_sve2

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
        if self.options.get_safe("build_decoder"):
            self.cpp_info.components["decoder"].libs = ["SvtAv1Dec"]
            self.cpp_info.components["decoder"].includedirs = ["include/svt-av1"]
            self.cpp_info.components["decoder"].set_property("pkg_config_name", "SvtAv1Dec")
            self.cpp_info.components["decoder"].requires = ["cpuinfo::cpuinfo"]
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.components["encoder"].system_libs = ["pthread", "dl", "m"]

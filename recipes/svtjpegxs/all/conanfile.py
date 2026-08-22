import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMake
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0.9"


class SvtJpegXsConan(ConanFile):
    name = "svtjpegxs"
    description = "A JPEG XS (ISO/IEC 21122) compatible software encoder/decoder library"
    license = "BSD-2-Clause-Patent"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenVisualCloud/SVT-JPEG-XS"
    topics = ("jpegxs", "codec", "encoder", "decoder", "image", "video")
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

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("yasm/1.3.0")

    def validate(self):
        if self.settings.arch not in ["x86", "x86_64"]:
            # INFO: The upstream mention about only supporting x86, SSE and AVX
            # https://github.com/OpenVisualCloud/SVT-JPEG-XS/tree/v0.9.0?tab=readme-ov-file#environment-and-requirements
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.arch}. Only x86 and x86_64 are supported.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_APPS"] = False
        if self.settings.os != "Windows":
            # INFO: The upstream use OBJECT library for shared library. CMake does not pass -fPIC to OBJECT library
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["SvtJpegxs"]
        self.cpp_info.set_property("pkg_config_name", "SvtJpegxs")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]

        if is_msvc(self) and self.options.shared:
            self.cpp_info.bindirs = ["lib"]
            self.cpp_info.defines.append("DEF_DLL")

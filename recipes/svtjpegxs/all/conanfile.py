import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, rmdir

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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        pass
        # if not self.settings.arch in ("x86", "x86_64"):
        #     self.tool_requires("simde/0.8.2")

    def build_requirements(self):
        self.tool_requires("yasm/1.3.0")

    def validate(self):
        check_min_cppstd(self, 11)

        if self.settings.arch not in ["x86", "x86_64"]:
            # INFO: The upstream mention about only supporting x86, SSE and AVX
            # https://github.com/OpenVisualCloud/SVT-JPEG-XS/tree/v0.9.0?tab=readme-ov-file#environment-and-requirements
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.arch}. Only x86 and x86_64 are supported.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_APPS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE.md"):
            copy(self, license_file, self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["SvtJpegxs"]

        self.cpp_info.set_property("pkg_config_name", "libSvtJpegxs")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")

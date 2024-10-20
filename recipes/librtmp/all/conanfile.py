import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file

required_conan_version = ">=1.53.0"


class LibrtmpConan(ConanFile):
    name = "librtmp"
    description = "RTMPDump Real-Time Messaging Protocol API"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://rtmpdump.mplayerhq.hu"
    topics = ("rtmpdump", "rtmp", "real-time messaging protocol")
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("openssl/[>=1.1 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RTMP_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["RTMP_VERSION"] = self.version
        tc.variables["RTMP_SOVERSION"] = 1
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # When _DEBUG macro is defined, there is some extra logging logic with strong expectations
        # in source code calling librtmp, something orthogonal to debugger.
        # _DEBUG macro is not a standard macro in most compilers, but it's automatically
        # defined by msvc in Debug mode, something librtmp didn't expect I guess.
        # So we replace this generic name by RTMP_DEBUGINFO
        for src_file in ("handshake.h", "log.c", "log.h", "rtmp.c"):
            replace_in_file(
                self,
                os.path.join(self.source_folder, "librtmp", src_file),
                "#ifdef _DEBUG",
                "#ifdef RTMP_DEBUGINFO",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "librtmp")
        self.cpp_info.libs = ["rtmp"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winmm", "ws2_32"])

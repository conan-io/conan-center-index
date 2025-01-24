import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class LibTomMathConan(ConanFile):
    name = "libtommath"
    description = "LibTomMath is a free open source portable number theoretic multiple-precision integer library written entirely in C."
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libtom.net/"
    topics = ("math", "multi-precision")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.settings.os == "Windows":
            self.package_type = "static-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def _patch_sources(self):
        if is_msvc(self):
            # libtommath requires /O1 on MSVC Debug builds for dead code elimination.
            # I could not find a way short of forcing settings.build_type=RelWithDebInfo to get that to work, though.
            # Disabling the missing symbols directly instead.
            # https://github.com/libtom/libtommath/blob/42b3fb07e7d504f61a04c7fca12e996d76a25251/s_mp_rand_platform.c#L120-L138
            file = "bn_s_mp_rand_platform.c" if Version(self.version) <= "1.3.0" else "s_mp_rand_platform.c"
            for symbol in ["s_read_getrandom", "s_read_ltm_rng", "s_read_arc4random", "s_read_urandom"]:
                replace_in_file(self, os.path.join(self.source_folder, file),
                                f"if ((err != MP_OKAY) && MP_HAS({symbol.upper()})",
                                f"// if ((err != MP_OKAY) && MP_HAS({symbol.upper()})")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libtommath")
        self.cpp_info.set_property("cmake_target_name", "libtommath")
        self.cpp_info.set_property("pkg_config_name", "libtommath")

        self.cpp_info.libs = ["tommath"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32", "crypt32"]

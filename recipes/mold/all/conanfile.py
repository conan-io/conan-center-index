import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv

required_conan_version = ">2.0"


class MoldConan(ConanFile):
    name = "mold"
    description = (
        "mold is a faster drop-in replacement for existing Unix linkers. "
        "It is several times faster than the LLVM lld linker."
    )
    license = ("AGPL-3.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rui314/mold/"
    topics = ("ld", "linkage", "compilation", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_mimalloc": [True, False],
    }
    default_options = {
        "with_mimalloc": False,
    }

    def configure(self):
        if Version(self.version) < "2.0.0":
            self.license = "AGPL-3.0"
        else:
            self.license = "MIT"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("xxhash/0.8.2")
        if self.options.with_mimalloc:
            self.requires("mimalloc/2.1.2")
        if Version(self.version) < "2.2.0":
            # Newer versions use vendored-in BLAKE3
            self.requires("openssl/[>=1.1 <4]")

    def package_id(self):
        del self.info.settings.compiler

    def validate_build(self):
        # perform these checks in validate_build() - since the compiler is removed from the package_id,
        # this lets the compatibility plugin consider the executable built with other compilers
        if Version(self.version) >= "2.34.0":
            # mold has required C+20 since 1.4.1. However, C++20 features are used for the first time in 2.34.0.
            check_min_cppstd(self, 20)
        if self.settings.compiler in ["gcc", "clang", "intel-cc"] and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration('Mold can only be built with libstdc++11; specify mold:compiler.libcxx=libstdc++11 in your build profile')
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration(f'{self.name} can not be built on {self.settings.os}.')
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration("GCC version 10 or higher required")
        if self.settings.compiler in ('clang', 'apple-clang') and Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration("Clang version 12 or higher required")
        if Version(self.version) >= "2.34.0" and self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration("Apple-Clang version 14 or higher required due to C++20 features")
        if self.settings.compiler == "apple-clang" and "armv8" == self.settings.arch :
            raise ConanInvalidConfiguration(f'{self.name} is still not supported by Mac M1.')
        if Version(self.version) == "2.33.0" and self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration(f'{self.ref} doesn\'t support Apple-Clang < 14.')

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18.0 <4]")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MOLD_USE_MIMALLOC"] = self.options.with_mimalloc
        tc.variables["MOLD_USE_SYSTEM_MIMALLOC"] = True
        tc.variables["MOLD_USE_SYSTEM_TBB"] = False # see https://github.com/conan-io/conan-center-index/pull/23575#issuecomment-2059154281
        tc.variables["CMAKE_INSTALL_LIBEXECDIR"] = "libexec"
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

        vbe = VirtualBuildEnv(self)
        vbe.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread", "dl"]

        bindir = os.path.join(self.package_folder, "bin")
        mold_executable = os.path.join(bindir, "mold")
        self.conf_info.define("user.mold:path", mold_executable)
        self.buildenv_info.define_path("MOLD_ROOT", bindir)
        self.buildenv_info.define("LD", mold_executable)

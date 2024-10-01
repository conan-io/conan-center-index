import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import XCRun, to_apple_arch, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class PbcConan(ConanFile):
    name = "pbc"
    description = ("The PBC (Pairing-Based Crypto) library is a C library providing "
                   "low-level routines for pairing-based cryptosystems.")
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://crypto.stanford.edu/pbc/"
    topics = ("crypto", "cryptography", "security", "pairings", "cryptographic")

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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("pbc is not compatible with MSVC due to use of GNU extensions")

    def build_requirements(self):
        self.tool_requires("flex/2.6.4")
        self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("LEX=flex")
        # No idea why this is necessary, but if you don't set CC this way, then
        # configure complains that it can't find gmp.
        if cross_building(self) and self.settings.compiler == "apple-clang":
            xcr = XCRun(self)
            target = to_apple_arch(self) + "-apple-darwin"
            min_ios = ""
            if self.settings.os == "iOS":
                min_ios = f"-miphoneos-version-min={self.settings.os.version}"
            tc.configure_args.append(f"CC={xcr.cc} -isysroot {xcr.sdk_path} -target {target} {min_ios}")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["pbc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

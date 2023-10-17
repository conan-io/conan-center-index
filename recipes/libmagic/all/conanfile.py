from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class LibmagicConan(ConanFile):
    name = "libmagic"
    description = "Magic number recognition library - detect files with data in particular fixed formats."
    license = "DocumentRef-COPYING:LicenseRef-BSD-2-Clause-File"  # Modified BSD 2-Clause that states no restrictions on US export
    homepage = "https://github.com/file/file"
    url = "https://github.com/conan-io/conan-center-index"
    topics = "magic", "file format"

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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("lzip/1.23")
        self.requires("xz_utils/5.4.2")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/1.5.5")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported yet")
        if cross_building(self):
            # TODO: Cross-compilation requires a build-context version of 'file' executable to be available.
            # It might be possible to build the project for the 'build' platform first to make it work.
            raise ConanInvalidConfiguration("Cross-compilation is not supported yet")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        # Set from 'auto' to explicitly enabled
        tc.configure_args.append("--enable-bzlib")
        tc.configure_args.append("--enable-lzlib")
        tc.configure_args.append("--enable-xzlib")
        tc.configure_args.append("--enable-zlib")
        tc.configure_args.append("--enable-zstdlib")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)
        rename(self, os.path.join(self.package_folder, "share", "misc"),
               os.path.join(self.package_folder, "res"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name",  "libmagic")
        self.cpp_info.libs = ["magic"]
        self.runenv_info.define_path("MAGIC", os.path.join(self.package_folder, "res", "magic.mgc"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

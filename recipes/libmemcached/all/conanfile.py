from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, get, copy, export_conandata_patches, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os

import os

required_conan_version = ">=1.54.0"

class LibmemcachedConan(ConanFile):
    name = "libmemcached"

    # Optional metadata
    license = "BSD License"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libmemcached.org/"
    description = "libmemcached is a C client library for interfacing to a memcached server"
    topics = ("cache", "network", "cloud")
    # package_type should usually be "library" (if there is shared option)
    package_type = "library"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sasl": [True, False]
    }
    default_options = {"shared": False,
                       "fPIC": True,
                       "sasl": False}

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                strip_root=True, destination=self.source_folder)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"] or not is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def _patch_source(self):
        apply_conandata_patches(self)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        tc.configure_args.append('--disable-dependency-tracking')
        if not self.options.sasl:
            tc.configure_args.append("--disable-sasl")
        tc.generate()

        AutotoolsDeps(self).generate()

    def build(self):
        self._patch_source()

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        autotools.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # In shared lib/executable files, autotools set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["memcached"]
        self.cpp_info.system_libs = ["m"]


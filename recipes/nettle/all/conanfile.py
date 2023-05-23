from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class NettleConan(ConanFile):
    name = "nettle"
    description = "The Nettle and Hogweed low-level cryptographic libraries"
    homepage = "https://www.lysator.liu.se/~nisse/nettle"
    topics = ("crypto", "low-level-cryptographic", "cryptographic")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "public_key": [True, False],
        "fat": [True, False],
        "x86_aesni": [True, False],
        "x86_shani": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "public_key": True,
        "fat": False,
        "x86_aesni": False,
        "x86_shani": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch != "x86_64":
            del self.options.x86_aesni
            del self.options.x86_shani
        if self.settings.arch != "x86_64" and not str(self.settings.arch).startswith("arm"):
            del self.options.fat

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.public_key:
            self.requires("gmp/6.2.1")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} cannot be built with Visual Studio")
        if Version(self.version) < "3.6" and self.options.get_safe("fat") and self.settings.arch == "x86_64":
            raise ConanInvalidConfiguration("fat support is broken on this nettle release (due to a missing x86_64/sha_ni/sha1-compress.asm source)")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--enable-public-key" if self.options.public_key else "--disable-public-key",
            "--enable-fat" if self.options.get_safe("fat") else "--disable-fat",
            "--enable-x86-aesni" if self.options.get_safe("x86_aesni") else "--disable-x86-aesni",
            "--enable-x86_sshni" if self.options.get_safe("x86_sshni") else "--disable-x86_sshni",
        ])
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def _patch_sources(self):
        makefile_in = os.path.join(self.source_folder, "Makefile.in")
        # discard subdirs
        replace_in_file(self, makefile_in,
                              "SUBDIRS = tools testsuite examples",
                              "SUBDIRS = ")
        # Fix broken tests for compilers like apple-clang with -Werror,-Wimplicit-function-declaration
        replace_in_file(self, os.path.join(self.source_folder, "aclocal.m4"),
                              "cat >conftest.c <<EOF",
                              "cat >conftest.c <<EOF\n#include <stdlib.h>")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        # srcdir in unix path causes some troubles in asm files on Windows
        if self._settings_build.os == "Windows":
            replace_in_file(self, os.path.join(self.build_folder, "config.m4"),
                                  unix_path(self, os.path.join(self.build_folder, self.source_folder)),
                                  os.path.join(self.build_folder, self.source_folder).replace("\\", "/"))
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "hogweed")

        self.cpp_info.components["libnettle"].set_property("pkg_config_name", "nettle")
        self.cpp_info.components["libnettle"].libs = ["nettle"]

        self.cpp_info.components["hogweed"].set_property("pkg_config_name", "hogweed")
        self.cpp_info.components["hogweed"].libs = ["hogweed"]
        self.cpp_info.components["hogweed"].requires = ["libnettle"]
        if self.options.public_key:
            self.cpp_info.components["hogweed"].requires.append("gmp::libgmp")

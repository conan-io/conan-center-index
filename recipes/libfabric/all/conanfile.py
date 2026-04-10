import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class LibfabricConan(ConanFile):
    name = "libfabric"
    description = ("Libfabric, also known as Open Fabrics Interfaces (OFI), "
                   "defines a communication API for high-performance parallel and distributed applications.")
    license = ("BSD-2-Clause", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libfabric.org"
    topics = ("fabric", "communication", "framework", "service")

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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows":
            # FIXME: libfabric provides msbuild project files.
            raise ConanInvalidConfiguration(f"{self.ref} Conan recipes is not supported on Windows. Contributions are welcome.")

    def build_requirements(self):
        # Used in ./configure tests and build
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--enable-debug")
        tc.configure_args.append("--with-libnl=no")
        tc.configure_args.append("--enable-lpp=no")
        if is_apple_os(self):
            tc.extra_ldflags.append("-headerpad_max_install_names")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        VirtualBuildEnv(self).generate()
        VirtualRunEnv(self).generate(scope="build")

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libfabric")
        self.cpp_info.libs = ["fabric"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m", "rt", "dl"]
        if self.settings.compiler in ["gcc", "clang"]:
            self.cpp_info.system_libs.append("atomic")

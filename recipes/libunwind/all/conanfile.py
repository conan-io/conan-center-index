from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout

import os
import shutil

required_conan_version = ">=1.53.0"

class LiunwindConan(ConanFile):
    name = "libunwind"
    description = "Manipulate the preserved state of each call-frame and resume the execution at any point."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libunwind/libunwind"
    topics = ("unwind", "debuggers", "exception-handling", "introspection", "setjmp")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "coredump": [True, False],
        "ptrace": [True, False],
        "setjmp": [True, False],
        "minidebuginfo": [True, False],
        "zlibdebuginfo": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "coredump": True,
        "ptrace": True,
        "setjmp": True,
        "minidebuginfo": True,
        "zlibdebuginfo": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.minidebuginfo:
            self.requires("xz_utils/5.6.1")
        if self.options.zlibdebuginfo:
            self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("libunwind is only supported on Linux and FreeBSD")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-coredump={yes_no(self.options.coredump)}",
            f"--enable-ptrace={yes_no(self.options.ptrace)}",
            f"--enable-setjmp={yes_no(self.options.setjmp)}",
            f"--enable-minidebuginfo={yes_no(self.options.minidebuginfo)}",
            f"--enable-zlibdebuginfo={yes_no(self.options.zlibdebuginfo)}",
            "--disable-tests",
            "--disable-documentation",
        ])
        tc.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

        # In install-exec-hook in Makefile.am, libunwind_generic is linked to libunwind_${arch}.
        # As this seems to be unnecessary for the conan package.
        # rename the real file to libunwind_generic,
        lib_ext = "so" if self.options.shared else "a"
        symlink_path = os.path.join(self.package_folder, "lib", f"libunwind-generic.{lib_ext}")
        source_path =  os.path.realpath(symlink_path)
        rm(self, os.path.basename(symlink_path), os.path.dirname(symlink_path))
        shutil.copy(source_path, symlink_path)

    def package_info(self):
        self.cpp_info.components["unwind"].set_property("pkg_config_name", "libunwind")
        self.cpp_info.components["unwind"].libs = ["unwind"]
        if self.options.minidebuginfo:
            self.cpp_info.components["unwind"].requires.append("xz_utils::xz_utils")
        if self.options.zlibdebuginfo:
            self.cpp_info.components["unwind"].requires.append("zlib::zlib")
        if self.settings.os == "Linux":
            self.cpp_info.components["unwind"].system_libs.append("pthread")
        self.cpp_info.components["generic"].set_property("pkg_config_name", "libunwind-generic")
        self.cpp_info.components["generic"].libs = ["unwind-generic"]
        self.cpp_info.components["generic"].requires = ["unwind"]
        if self.options.ptrace:
            self.cpp_info.components["ptrace"].set_property("pkg_config_name", "libunwind-ptrace")
            self.cpp_info.components["ptrace"].libs = ["unwind-ptrace"]
            self.cpp_info.components["ptrace"].requires = ["generic", "unwind"]
        if self.options.setjmp:
            self.cpp_info.components["setjmp"].set_property("pkg_config_name", "libunwind-setjmp")
            self.cpp_info.components["setjmp"].libs = ["unwind-setjmp"]
            self.cpp_info.components["setjmp"].requires = ["unwind"]
        if self.options.coredump:
            self.cpp_info.components["coredump"].set_property("pkg_config_name", "libunwind-coredump")
            self.cpp_info.components["coredump"].libs = ["unwind-coredump"]
            self.cpp_info.components["coredump"].requires = ["generic", "unwind"]

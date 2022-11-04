from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

import os

required_conan_version = ">=1.53.0"

class LiunwindConan(ConanFile):
    name = "libunwind"
    description = "Manipulate the preserved state of each call-frame and resume the execution at any point."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libunwind/libunwind"
    topics = ("unwind", "debuggers", "exception-handling", "introspection", "setjmp")
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

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
            self.requires("xz_utils/5.2.5")
        if self.options.zlibdebuginfo:
            self.requires("zlib/1.2.13")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("libunwind is only supported on Linux and FreeBSD")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
            f"--enable-coredump={yes_no(self.options.coredump)}",
            f"--enable-ptrace={yes_no(self.options.ptrace)}",
            f"--enable-setjmp={yes_no(self.options.setjmp)}",
            f"--enable-minidebuginfo={yes_no(self.options.minidebuginfo)}",
            f"--enable-zlibdebuginfo={yes_no(self.options.zlibdebuginfo)}",
            "--disable-tests",
            "--disable-documentation",
        ])
        tc.generate()

        tc = PkgConfigDeps(self)
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
        rename(self, source_path, symlink_path)

    def package_info(self):
        self.cpp_info.components["unwind"].names["pkg_config"] = "libunwind"
        self.cpp_info.components["unwind"].libs = ["unwind"]
        if self.options.minidebuginfo:
            self.cpp_info.components["unwind"].requires.append("xz_utils::xz_utils")
        if self.options.zlibdebuginfo:
            self.cpp_info.components["unwind"].requires.append("zlib::zlib")
        if self.settings.os == "Linux":
            self.cpp_info.components["unwind"].system_libs.append("pthread")
        self.cpp_info.components["generic"].names["pkg_config"] = "libunwind-generic"
        self.cpp_info.components["generic"].libs = ["unwind-generic"]
        self.cpp_info.components["generic"].requires = ["unwind"]
        if self.options.ptrace:
            self.cpp_info.components["ptrace"].names["pkg_config"] = "libunwind-ptrace"
            self.cpp_info.components["ptrace"].libs = ["unwind-ptrace"]
            self.cpp_info.components["ptrace"].requires = ["generic", "unwind"]
        if self.options.setjmp:
            self.cpp_info.components["setjmp"].names["pkg_config"] = "libunwind-setjmp"
            self.cpp_info.components["setjmp"].libs = ["unwind-setjmp"]
            self.cpp_info.components["setjmp"].requires = ["unwind"]
        if self.options.coredump:
            self.cpp_info.components["coredump"].names["pkg_config"] = "libunwind-coredump"
            self.cpp_info.components["coredump"].libs = ["unwind-coredump"]
            self.cpp_info.components["coredump"].requires = ["generic", "unwind"]

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.54.0"


class GdbmConan(ConanFile):
    name = "gdbm"
    description = ("gdbm is a library of database functions that uses "
                   "extensible hashing and work similar to "
                   "the standard UNIX dbm. "
                   "These routines are provided to a programmer needing "
                   "to create and manipulate a hashed database.")
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org.ua/software/gdbm/gdbm.html"
    topics = ("dbm", "hash", "database")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "libgdbm_compat": [True, False],
        "gdbmtool_debug": [True, False],
        "with_libiconv": [True, False],
        "with_readline": [True, False],
        "with_nls": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "libgdbm_compat": False,
        "gdbmtool_debug": True,
        "with_libiconv": False,
        "with_readline": False,
        "with_nls": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if not self.options.with_nls:
            self.options.rm_safe("with_libiconv")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_libiconv"):
            self.requires("libiconv/1.17")
        if self.options.with_readline:
            self.requires("readline/8.1.2")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.name} is not supported on Windows")

    def build_requirements(self):
        self.tool_requires("bison/3.8.2")
        self.tool_requires("flex/2.6.4")
        self.tool_requires("gnu-config/cci.20210814")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        if not cross_building(self):
            virtual_run_env = VirtualRunEnv(self)
            virtual_run_env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        enable_debug = self.settings.build_type in ["Debug", "RelWithDebInfo"]
        tc.configure_args.extend([
            f"--enable-debug={yes_no(enable_debug)}",
            f"--enable-libgdbm-compat={yes_no(self.options.libgdbm_compat)}",
            f"--enable-gdbmtool-debug={yes_no(self.options.gdbmtool_debug)}",
            f"--enable-nls={yes_no(self.options.with_nls)}",
            f"--with-readline={yes_no(self.options.with_readline)}",
            f"--with-pic={yes_no(self.options.get_safe('fPIC', True))}",
        ])
        if self.options.get_safe("with_libiconv"):
            libiconv_package_folder = self.dependencies.direct_host["libiconv"].package_folder
            tc.configure_args.extend([
                f"--with-libiconv-prefix={libiconv_package_folder}"
                "--with-libintl-prefix"
            ])
        else:
            tc.configure_args.extend([
                "--without-libiconv-prefix",
                "--without-libintl-prefix"
            ])
        tc.generate()
        autotools_deps = AutotoolsDeps(self)
        autotools_deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), os.path.dirname(gnu_config), os.path.join(self.source_folder, "build-aux"))

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make(target="maintainer-clean-generic")
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        if self.options.libgdbm_compat:
            self.cpp_info.libs.append("gdbm_compat")
        self.cpp_info.libs.append("gdbm")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

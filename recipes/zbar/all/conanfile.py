from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, copy, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class ZbarConan(ConanFile):
    name = "zbar"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://zbar.sourceforge.net/"
    topics = ("barcode", "scanner", "decoder", "reader", "bar")
    description = "ZBar is an open source software suite for reading bar codes\
                   from various sources, such as video streams, image files and raw intensity sensors"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_video": [True, False],
        "with_imagemagick": [True, False],
        "with_gtk": [True, False],
        "with_qt": [True, False],
        "with_python_bindings": [True, False],
        "with_x": [True, False],
        "with_xshm": [True, False],
        "with_xv": [True, False],
        "with_jpeg": [True, False],
        "enable_pthread": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_video": False,
        "with_imagemagick": False,
        "with_gtk": False,
        "with_qt": False,
        "with_python_bindings": False,
        "with_x": False,
        "with_xshm": False,
        "with_xv": False,
        "with_jpeg": False,
        "enable_pthread": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_imagemagick:
            self.requires("imagemagick/7.0.11-14")
        if self.options.with_gtk:
            self.requires("gtk/4.7.0")
        if self.options.with_qt:
            self.requires("qt/5.15.9")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Zbar can't be built on Windows")
        if is_apple_os(self) and not self.options.shared:
            raise ConanInvalidConfiguration("Zbar can't be built static on macOS")
        if self.options.with_xv:            #TODO add when available
            self.output.warning("There is no Xvideo package available on Conan (yet). This recipe will use the one present on the system (if available).")
        if Version(self.version) >= "0.22" and cross_building(self):
            raise ConanInvalidConfiguration(f"{self.ref} can't be built on cross building environment currently because autopoint(part of gettext) doesn't execute correctly.")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if Version(self.version) >= "0.22":
            self.tool_requires("gettext/0.21")
            self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--enable-video={yes_no(self.options.with_video)}",
            f"--with-imagemagick={yes_no(self.options.with_imagemagick)}",
            f"--with-gtk={yes_no(self.options.with_gtk)}",
            f"--with-qt={yes_no(self.options.with_qt)}",
            f"--with-python={yes_no(self.options.with_python_bindings)}",
            f"--with-x={yes_no(self.options.with_x)}",
            f"--with-xshm={yes_no(self.options.with_xshm)}",
            f"--with-xv={yes_no(self.options.with_xv)}",
            f"--with-jpeg={yes_no(self.options.with_jpeg)}",
            f"--enable-pthread={yes_no(self.options.enable_pthread)}",
        ])
        env = tc.environment()
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # ./libtool: eval: line 961: syntax error near unexpected token `|'
            env.define("NM", "nm")
        tc.generate(env)

        AutotoolsDeps(self).generate()
        PkgConfigDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config),
                           src=os.path.dirname(gnu_config),
                           dst=os.path.join(self.source_folder, "config"))

        autotools = Autotools(self)
        if Version(self.version) >= "0.22":
            autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["zbar"]
        self.cpp_info.set_property("pkg_config_name", "zbar")
        if self.settings.os in ("FreeBSD", "Linux") and self.options.enable_pthread:
            self.cpp_info.system_libs = ["pthread"]

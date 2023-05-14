from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.files import get, copy, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import Environment
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class ZbarConan(ConanFile):
    name = "zbar"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://zbar.sourceforge.net/"
    topics = ("zbar", "barcode", "scanner", "decoder", "reader", "bar")
    description = "ZBar is an open source software suite for reading bar codes\
                   from various sources, such as video streams, image files and raw intensity sensors"
    settings = "os", "compiler", "build_type", "arch"
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
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_imagemagick:
            self.requires("imagemagick/7.0.11-14")
        if self.options.with_gtk:
            self.requires("gtk/4.7.0")
        if self.options.with_qt:
            self.requires("qt/5.15.9")
        if Version(self.version) >= "0.22":
            self.requires("libiconv/1.17")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        if Version(self.version) >= "0.22":
            self.tool_requires("gettext/0.21")
            self.tool_requires("libtool/2.4.7")
            self.tool_requires("pkgconf/1.9.3")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Zbar can't be built on Windows")
        if is_apple_os(self) and not self.options.shared:
            raise ConanInvalidConfiguration("Zbar can't be built static on macOS")
        if self.options.with_xv:            #TODO add when available
            self.output.warn("There is no Xvideo package available on Conan (yet). This recipe will use the one present on the system (if available).")
        if Version(self.version) >= "0.22" and cross_building(self):
            raise ConanInvalidConfiguration(f"{self.ref} can't be built on cross building environment currently because autopoint(part of gettext) doesn't execute correctly.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
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
        tc.generate()
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # ./libtool: eval: line 961: syntax error near unexpected token `|'
            env = Environment()
            env.define("NM", "nm")
            env.vars(self).save_script("conanbuild_macos_nm")

    def build(self):
        apply_conandata_patches(self)
        copy(self, "config.sub", src=self.source_folder, dst=os.path.join(self.source_folder, "config"))
        copy(self, "config.guess", src=self.source_folder, dst=os.path.join(self.source_folder, "config"))

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
        if is_apple_os(self):
            self.cpp_info.system_libs = ["iconv"]

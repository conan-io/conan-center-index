from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.files import get, copy, rmdir, rm, collect_libs
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class ZbarConan(ConanFile):
    name = "zbar"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://zbar.sourceforge.net/"
    topics = ("zbar", "bar codes")
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

    _autotools = None

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", None) or self.deps_user_info

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_imagemagick:
            self.requires("imagemagick/7.0.11-14")
        if self.options.with_gtk:
            self.requires("gtk/4.7.0")
        if self.options.with_qt:
            self.requires("qt/5.15.5")
        if Version(self.version) >= "0.22":
            self.requires("libiconv/1.17")

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20210814")
        if Version(self.version) >= "0.22":
            self.build_requires("automake/1.16.5")
            self.build_requires("gettext/0.21")
            self.build_requires("pkgconf/1.7.4")
            self.build_requires("libtool/2.4.6")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Zbar can't be built on Windows")
        if is_apple_os(self) and not self.options.shared:
            raise ConanInvalidConfiguration("Zbar can't be built static on macOS")
        if self.options.with_xv:            #TODO add when available
            self.output.warn("There is no Xvideo package available on Conan (yet). This recipe will use the one present on the system (if available).")
        if Version(self.version) >= "0.22" and cross_building(self):
            raise ConanInvalidConfiguration("{} can't be built on cross building environment currently because autopoint(part of gettext) doesn't execute correctly.".format(self.name))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = Autotools(self)
            if Version(self.version) >= "0.22":
                self._autotools.autoreconf(args=['--verbose'])
            yes_no = lambda v: "yes" if v else "no"
            args = [
                "--enable-shared={}".format(yes_no(self.options.shared)),
                "--enable-static={}".format(yes_no(not self.options.shared)),
                "--enable-video={}".format(yes_no(self.options.with_video)),
                "--with-imagemagick={}".format(yes_no(self.options.with_imagemagick)),
                "--with-gtk={}".format(yes_no(self.options.with_gtk)),
                "--with-qt={}".format(yes_no(self.options.with_qt)),
                "--with-python={}".format(yes_no(self.options.with_python_bindings)),
                "--with-x={}".format(yes_no(self.options.with_x)),
                "--with-xshm={}".format(yes_no(self.options.with_xshm)),
                "--with-xv={}".format(yes_no(self.options.with_xv)),
                "--with-jpeg={}".format(yes_no(self.options.with_jpeg)),
                "--enable-pthread={}".format(yes_no(self.options.enable_pthread)),
            ]
            if self.settings.os == "Macos" and self.settings.arch == "armv8":
               # ./libtool: eval: line 961: syntax error near unexpected token `|'
                args.append("NM=nm")
            self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        copy(self, "config.sub", src=self.source_folder, dst=os.path.join(self.source_folder, "config"))
        copy(self, "config.guess", src=self.source_folder, dst=os.path.join(self.source_folder, "config"))

        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        if Version(self.version) < "0.23":
            copy(self, "LICENSE", src=self.source_folder, dst="licenses")
        else:
            copy(self, "LICENSE.md", src=self.source_folder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "zbar"
        self.cpp_info.set_property("pkg_config_name", "zbar")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ("FreeBSD", "Linux") and self.options.enable_pthread:
            self.cpp_info.system_libs = ["pthread"]
        if is_apple_os(self):
            self.cpp_info.system_libs = ["iconv"]

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment

required_conan_version = ">=1.33.0"


class LibGphoto2(ConanFile):
    name = "libgphoto2"
    url = "https://github.com/gphoto/libgphoto2"
    description = "The libgphoto2 camera access and control library."
    homepage = "http://www.gphoto.org/"
    license = "LGPL-2.1"
    topics = ("gphoto2", "libgphoto2", "libgphoto", "photo")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libusb": [True, False],
        "with_libcurl": [True, False],
        "with_libxml2": [True, False],
        "with_libexif": [True, False],
        "with_libjpeg": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libusb": True,
        "with_libcurl": True,
        "with_libxml2": True,
        "with_libexif": True,
        "with_libjpeg": True,
    }
    generators = "pkg_config"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("libtool/2.4.6")

    def requirements(self):
        if self.options.with_libusb:
            self.requires("libusb/1.0.24")
        if self.options.with_libcurl:
            self.requires("libcurl/7.74.0")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.10")
        if self.options.with_libexif:
            self.requires("libexif/0.6.23")
        if self.options.with_libjpeg:
            self.requires("libjpeg/9d")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-libcurl={}".format(yes_no(self.options.with_libcurl)),
            "--with-libexif={}".format(yes_no(self.options.with_libexif)),
            "--with-libxml-2.0={}".format(yes_no(self.options.with_libxml2)),
            "--disable-nls",
        ]
        if not self.options.with_libjpeg:
            args.extend(["--without-jpeg"])

        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("print-camera-list", "bin", "packaging/generic/.libs")

    def package_info(self):
        self.cpp_info.libs = ["gphoto2", "gphoto2_port"]

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibGphoto2(ConanFile):
    name = "libgphoto2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The libgphoto2 camera access and control library."
    homepage = "http://www.gphoto.org/"
    license = "LGPL-2.1"
    topics = ("gphoto2", "libgphoto2", "libgphoto", "photo")
    exports_sources = "patches/*"
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
        "shared": True,
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

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def validate(self):
        if not self.options.shared:
            raise ConanInvalidConfiguration("building libgphoto2 as a static library is not supported")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("libgphoto2 does not support Windows")

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.os == "Linux" and not self.options["libtool"].shared:
            env = {
                "LIBLTDL": "-lltdl -ldl",
            }
            with tools.environment_append(env):
                yield
        else:
            yield

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("libtool/2.4.6")
        if self.options.with_libusb:
            self.requires("libusb/1.0.26")
        if self.options.with_libcurl:
            self.requires("libcurl/7.83.1")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.14")
        if self.options.with_libexif:
            self.requires("libexif/0.6.23")
        if self.options.with_libjpeg:
            self.requires("libjpeg/9d")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        auto_no = lambda v: "auto" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-libcurl={}".format(auto_no(self.options.with_libcurl)),
            "--with-libexif={}".format(auto_no(self.options.with_libexif)),
            "--with-libxml-2.0={}".format(auto_no(self.options.with_libxml2)),
            "--disable-nls",
            "--datadir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
            "udevscriptdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
            "utilsdir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin"))),
        ]
        if not self.options.with_libjpeg:
            args.append("--without-jpeg")
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rm(self, self.package_folder, "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gphoto2", "gphoto2_port"]
        self.cpp_info.names["pkg_config"] = "libgphoto2"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]


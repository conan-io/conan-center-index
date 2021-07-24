from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PupnpConan(ConanFile):
    name = "pupnp"
    description = (
        "The portable Universal Plug and Play (UPnP) SDK "
        "provides support for building UPnP-compliant control points, "
        "devices, and bridges on several operating systems."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pupnp/pupnp"
    topics = ("conan", "upnp", "networking")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ipv6": [True, False],
        "reuseaddr": [True, False],
        "webserver": [True, False],
        "client": [True, False],
        "device": [True, False],
        "largefile": [True, False],
        "tools": [True, False],
        "blocking-tcp": [True, False],
        "debug":  [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ipv6": True,
        "reuseaddr": True,
        "webserver": True,
        "client": True,
        "device": True,
        "largefile": True,
        "tools": True,
        "blocking-tcp": False,
        "debug": True # Actually enables logging routines...
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Windows":
            # Note, pupnp has build instructions for Windows but they
            # include VC 6 and require pthreads-w32 library.
            # Someone who needs it and has possibility to build it could step in.
            raise ConanInvalidConfiguration("Windows builds are not supported.")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._autotools:
            args = [
                "--enable-static=%s" % ("no" if self.options.shared else "yes"),
                "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
                "--disable-samples",
            ]

            def enable_disable(opt):
                what = "enable" if getattr(self.options, opt) else "disable"
                return "--{}-{}".format(what, opt)

            args.extend(
                map(
                    enable_disable,
                    (
                        "ipv6",
                        "reuseaddr",
                        "webserver",
                        "client",
                        "device",
                        "largefile",
                        "tools",
                        "blocking-tcp",
                        "debug"
                    ),
                )
            )

            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")))
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["upnp", "ixml"]
        self.cpp_info.includedirs.append(os.path.join("include", "upnp"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread"])
            self.cpp_info.cflags.extend(["-pthread"])
            self.cpp_info.cxxflags.extend(["-pthread"])

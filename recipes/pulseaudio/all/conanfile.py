from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class PulseAudioConan(ConanFile):
    name = "pulseaudio"
    description = "PulseAudio is a sound system for POSIX OSes, meaning that it is a proxy for sound applications."
    topics = ("conan", "pulseaudio", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pulseaudio.org/"
    license = "LGPL-2.1"

    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_alsa": [True, False],
        "with_glib": [True, False],
        "with_fftw": [True, False],
        "with_x11": [True, False],
        "with_openssl": [True, False],
        "with_dbus": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_alsa": True,
        "with_glib": False,
        "with_fftw": False,
        "with_x11": True,
        "with_openssl": True,
        "with_dbus": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("pulseaudio supports only linux currently")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self.options.with_dbus:
            del self.options.with_fftw

    def requirements(self):
        self.requires("libsndfile/1.0.30")
        self.requires("libcap/2.46")
        if self.options.with_alsa:
            self.requires("libalsa/1.2.4")
        if self.options.with_glib:
            self.requires("glib/2.67.3")
        if self.options.get_safe("with_fftw"):
            self.requires("fftw/3.3.9")
        if self.options.with_x11:
            self.requires("xorg/system")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1i")
        if self.options.with_dbus:
            self.requires("dbus/1.12.20")

    def validate(self):
        if self.options.get_safe("with_fftw") and self.options["fftw"].precision != "single":
            raise ConanInvalidConfiguration("Pulse audio cannot use fftw %s precision."
                                            "Either set option fftw:precision=single"
                                            "or pulseaudio:with_fftw=False"
                                            % self.options["fftw"].precision)

    def build_requirements(self):
        self.build_requires("gettext/0.20.1")
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            args=[]

            for lib in ["alsa", "x11", "openssl", "dbus"]:
                args.append("--%s-%s" % ("enable" if getattr(self.options, "with_" + lib) else "disable", lib))
            args.append("--%s-glib2" % ("enable" if self.options.with_glib else "disable"))
            args.append("--%s-fftw" % ("with" if self.options.get_safe("with_fftw") else "without"))
            if self.options.shared:
                args.extend(["--enable-shared=yes", "--enable-static=no"])
            else:
                args.extend(["--enable-shared=no", "--enable-static=yes"])
            args.append("--with-udev-rules-dir=%s" % os.path.join(self.package_folder, "bin", "udev", "rules.d"))
            args.append("--with-systemduserunitdir=%s" % os.path.join(self.build_folder, "ignore"))
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.run_environment(self):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.run_environment(self):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(self.package_folder, "*.la")

    def package_info(self):
        self.cpp_info.libdirs = ["lib", os.path.join("lib", "pulseaudio")]
        if self.options.with_glib:
            self.cpp_info.libs.append("pulse-mainloop-glib")
        self.cpp_info.libs.extend(["pulse-simple", "pulse"])
        if not self.options.shared:
            self.cpp_info.libs.append("pulsecommon-%s" % self.version)
        self.cpp_info.defines = ["_REENTRANT"]
        self.cpp_info.names["pkg_config"] = "libpulse"
        # FIXME: add cmake generators when conan can generate PULSEAUDIO_INCLUDE_DIR PULSEAUDIO_LIBRARY vars

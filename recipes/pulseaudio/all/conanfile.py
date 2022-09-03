from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class PulseAudioConan(ConanFile):
    name = "pulseaudio"
    description = "PulseAudio is a sound system for POSIX OSes, meaning that it is a proxy for sound applications."
    topics = "sound",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pulseaudio.org/"
    license = "LGPL-2.1"

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        if not self.options.with_dbus:
            del self.options.with_fftw

    def requirements(self):
        self.requires("libiconv/1.17")
        self.requires("libsndfile/1.0.31")
        self.requires("libcap/2.65")
        self.requires("libtool/2.4.7")
        if self.options.with_alsa:
            self.requires("libalsa/1.2.7.2")
        if self.options.with_glib:
            self.requires("glib/2.73.3")
        if self.options.get_safe("with_fftw"):
            self.requires("fftw/3.3.9")
        if self.options.with_x11:
            self.requires("xorg/system")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_dbus:
            self.requires("dbus/1.12.20")

    def validate(self):
        if self.info.settings.os != "Linux":
            raise ConanInvalidConfiguration("pulseaudio supports only linux currently")

        if self.options.get_safe("with_fftw"):
            fftw_precision = self.dependencies["fftw"].options.precision
            if fftw_precision != "single":
                raise ConanInvalidConfiguration(
                    f"Pulse audio cannot use fftw {fftw_precision} precision. "
                    "Either set option fftw:precision=single or pulseaudio:with_fftw=False"
                )

    def build_requirements(self):
        self.tool_requires("gettext/0.21")
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
            f"--enable-glib2={yes_no(self.options.with_glib)}",
            f"--with-fftw={yes_no(self.options.get_safe('with_fftw'))}",
            f"--with-udev-rules-dir={os.path.join(self.package_folder, 'bin', 'udev', 'rules.d')}",
            f"--with-systemduserunitdir={os.path.join(self.build_folder, 'ignore')}",
        ])
        for lib in ["alsa", "x11", "openssl", "dbus"]:
            tc.configure_args.append(f"--enable-{lib}={yes_no(getattr(self.options, 'with_' + lib))}")
        # TODO: to remove when automatically handled by AutotoolsToolchain
        tc.configure_args.append("--libexecdir=${prefix}/bin")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()
        pkg = PkgConfigDeps(self)
        pkg.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.components["pulse"].set_property("pkg_config_name", "libpulse")
        self.cpp_info.components["pulse"].libs = ["pulse"]
        if not self.options.shared:
            self.cpp_info.components["pulse"].libs.append(f"pulsecommon-{self.version}")
        self.cpp_info.components["pulse"].libdirs.append(os.path.join("lib", "pulseaudio"))
        self.cpp_info.components["pulse"].requires = ["libiconv::libiconv", "libsndfile::libsndfile", "libcap::libcap", "libtool::libtool"]
        if self.options.with_alsa:
            self.cpp_info.components["pulse"].requires.append("libalsa::libalsa")
        if self.options.get_safe("with_fftw"):
            self.cpp_info.components["pulse"].requires.append("fftw::fftw")
        if self.options.with_x11:
            self.cpp_info.components["pulse"].requires.append("xorg::xorg")
        if self.options.with_openssl:
            self.cpp_info.components["pulse"].requires.append("openssl::openssl")
        if self.options.with_dbus:
            self.cpp_info.components["pulse"].requires.append("dbus::dbus")

        self.cpp_info.components["pulse-simple"].set_property("pkg_config_name", "libpulse-simple")
        self.cpp_info.components["pulse-simple"].libs = ["pulse-simple"]
        self.cpp_info.components["pulse-simple"].defines.append("_REENTRANT")
        self.cpp_info.components["pulse-simple"].requires = ["pulse"]

        if self.options.with_glib:
            self.cpp_info.components["pulse-mainloop-glib"].set_property("pkg_config_name", "libpulse-mainloop-glib")
            self.cpp_info.components["pulse-mainloop-glib"].libs = ["pulse-mainloop-glib"]
            self.cpp_info.components["pulse-mainloop-glib"].defines.append("_REENTRANT")
            self.cpp_info.components["pulse-mainloop-glib"].requires = ["pulse", "glib::glib-2.0"]

        # FIXME: add cmake generators when conan can generate PULSEAUDIO_INCLUDE_DIR PULSEAUDIO_LIBRARY vars

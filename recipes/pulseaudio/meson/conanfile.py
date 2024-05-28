from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class PulseAudioConan(ConanFile):
    name = "pulseaudio"
    description = "PulseAudio is a sound system for POSIX OSes, meaning that it is a proxy for sound applications."
    topics = ("sound", "audio", "sound-server")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pulseaudio.org/"
    license = "LGPL-2.1"

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_glib": [True, False],
        "with_fftw": [True, False],
        "with_x11": [True, False],
        "with_openssl": [True, False],
        "with_dbus": [True, False],
    }
    default_options = {
        "with_glib": False,
        "with_fftw": False,
        "with_x11": True,
        "with_openssl": True,
        "with_dbus": False,
    }

    def config_options(self):
        if self.settings.os not in ['Linux', 'FreeBSD']:
            del self.options.with_x11

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if not self.options.with_dbus:
            del self.options.with_fftw

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libgettext/0.22")
        self.requires("libiconv/1.17")
        self.requires("libsndfile/1.2.2")
        if self.options.with_glib:
            self.requires("glib/2.78.1")
        if self.options.get_safe("with_fftw"):
            self.requires("fftw/3.3.10")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_dbus:
            self.requires("dbus/1.15.8")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} recipe is only compatible with Linux right now. Contributions are welcome.")

        if self.options.get_safe("with_fftw"):
            if not self.dependencies["fftw"].options.precision_single:
                raise ConanInvalidConfiguration(
                     "Pulse audio uses fftw single precision. "
                     "Either set option -o fftw/*:precision_single=True or -o pulseaudio/*:with_fftw=False"
                )

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = MesonToolchain(self)
        tc.project_options['udevrulesdir']="${prefix}/bin/udev/rules.d"
        tc.project_options['systemduserunitdir'] = os.path.join(self.build_folder, 'ignore')
        for lib in ["x11", "openssl", "dbus", "glib", "fftw"]:
            tc.project_options[lib] = "enabled" if self.options.get_safe(f"with_{lib}") else "disabled"
        tc.project_options['database'] = 'simple'
        tc.project_options['tests'] = False
        tc.project_options['man'] = False
        tc.project_options['doxygen'] = False
        tc.project_options["daemon"] = False
        tc.generate()
        pkg = PkgConfigDeps(self)
        pkg.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.components["pulse"].set_property("pkg_config_name", "libpulse")
        self.cpp_info.components["pulse"].libs = ["pulse", f"pulsecommon-{self.version}"]
        self.cpp_info.components["pulse"].libdirs.append(os.path.join("lib", "pulseaudio"))
        self.cpp_info.components["pulse"].requires = ["libiconv::libiconv", "libsndfile::libsndfile", "libgettext::libgettext"]
        if self.options.get_safe("with_fftw"):
            self.cpp_info.components["pulse"].requires.append("fftw::fftw")
        if self.options.get_safe("with_x11"):
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

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
import os

required_conan_version = ">=1.53.0"


class PulseAudioConan(ConanFile):
    name = "pulseaudio"
    description = "PulseAudio is a sound system for POSIX OSes, meaning that it is a proxy for sound applications."
    topics = ("sound",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pulseaudio.org/"
    license = "LGPL-2.1"

    package_type = "library"
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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if not self.options.with_dbus:
            del self.options.with_fftw

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")
        self.requires("libsndfile/1.2.2")
        self.requires("libcap/2.69")
        self.requires("libtool/2.4.7")
        if self.options.with_alsa:
            self.requires("libalsa/1.2.10")
        if self.options.with_glib:
            self.requires("glib/2.78.0")
        if self.options.get_safe("with_fftw"):
            self.requires("fftw/3.3.10")
        if self.options.with_x11:
            self.requires("xorg/system")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_dbus:
            self.requires("dbus/1.15.8")

    def validate(self):
        # TODO: The newer Meson build system should support Windows
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("pulseaudio supports only linux currently")

        if self.options.get_safe("with_fftw"):
            fftw_precision = self.dependencies["fftw"].options.precision
            if fftw_precision != "single":
                raise ConanInvalidConfiguration(
                    f"Pulse audio cannot use fftw {fftw_precision} precision. "
                    "Either set option fftw:precision=single or pulseaudio:with_fftw=False"
                )

    def build_requirements(self):
        self.tool_requires("meson/1.2.3")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        def format_enabled(enabled):
            return "enabled" if enabled else "disabled"

        tc = MesonToolchain(self)
        tc.project_options["glib"] = format_enabled(self.options.with_glib)
        tc.project_options["fftw"] = format_enabled(self.options.get_safe("with_fftw", False))
        tc.project_options["x11"] = format_enabled(self.options.with_x11)
        tc.project_options["openssl"] = format_enabled(self.options.with_openssl)
        tc.project_options["dbus"] = format_enabled(self.options.with_dbus)
        tc.project_options["alsa"] = format_enabled(self.options.with_alsa)
        if self.options.with_alsa:
            tc.project_options["alsadatadir"] = os.path.join(self.dependencies["libalsa"].cpp_info.resdirs[0])
        tc.project_options["systemduserunitdir"] = os.path.join(self.build_folder, "ignore")
        tc.project_options["udevrulesdir"] = "${prefix}/bin/udev/rules.d"
        tc.project_options["libexecdir"] = "${prefix}/bin"

        tc.project_options["tests"] = "false"
        tc.project_options["doxygen"] = "false"
        tc.project_options["man"] = "false"
        # TODO: add support for the daemon component
        tc.project_options["daemon"] = "false"
        # tc.project_options["database"] = self.options.database
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
        # CMake target names are based on KDE: https://api.kde.org/ecm/find-module/FindPulseAudio.html
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "PulseAudio")
        self.cpp_info.set_property("cmake_target_name", "PulseAudio::PulseAudio")

        self.cpp_info.components["pulse"].libs = ["pulse", f"pulsecommon-{self.version}"]
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

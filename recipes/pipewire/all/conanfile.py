import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    load,
    rm,
    rmdir,
    save,
)
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=1.64.0 <2 || >=2.2.0"


class PipeWireConan(ConanFile):
    name = "pipewire"
    description = "PipeWire is a server and user space API to deal with multimedia pipelines."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pipewire.org/"
    topics = ("audio", "graph", "pipeline", "stream", "video")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "flatpak": [True, False],
        "gsettings": [True, False],
        "raop": [True, False],
        "with_avahi": [True, False],
        "with_dbus": [True, False],
        "with_ffmpeg": [True, False],
        "with_libalsa": [True, False],
        "with_libsndfile": [True, False],
        "with_libudev": [True, False],
        "with_ncurses": [True, False],
        "with_opus": [True, False],
        "with_pulseaudio": [True, False],
        "with_readline": [True, False],
        "with_selinux": [True, False],
        "with_vulkan": [True, False],
        "with_x11": [True, False],
        "with_xfixes": [True, False],
    }
    default_options = {
        "flatpak": True,
        "gsettings": True,
        "raop": True,
        "with_avahi": True,
        "with_dbus": True,
        "with_ffmpeg": False,
        "with_libalsa": True,
        "with_libsndfile": True,
        "with_libudev": True,
        "with_ncurses": True,
        "with_opus": True,
        "with_pulseaudio": True,
        "with_readline": True,
        "with_selinux": True,
        "with_vulkan": True,
        "with_x11": True,
        "with_xfixes": True,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        # The xfixes from the xorg/system package on CCI is version 5.0.1 which is too old for PipeWire which requires at least version 6.
        if os.getenv("CONAN_CENTER_BUILD_SERVICE") is not None:
            self.options.with_xfixes = False

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if self.options.with_libalsa:
            self.options.rm_safe("with_libudev")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("linux-headers-generic/6.5.9")
        if self.options.flatpak or self.options.gsettings:
            self.requires("glib/2.78.3")
        if self.options.raop:
            self.requires("openssl/3.2.1")
        if self.options.with_avahi:
            self.requires("avahi/0.8")
        if self.options.with_dbus:
            self.requires("dbus/1.15.8")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.1")
        if self.options.with_libalsa:
            self.requires("libalsa/1.2.10")
        if self.options.with_libsndfile:
            self.requires("libsndfile/1.2.2")
        if self.options.get_safe("with_libudev", True):
            self.requires("libudev/system")
        if self.options.with_ncurses:
            self.requires("ncurses/6.4")
        if self.options.with_opus:
            self.requires("opus/1.4")
        if self.options.with_pulseaudio:
            self.requires("pulseaudio/14.2")
        if self.options.with_readline:
            self.requires("readline/8.2")
        if self.options.with_selinux:
            self.requires("libselinux/3.5")
        if self.options.with_vulkan:
            self.requires("libdrm/2.4.119")
            self.requires("vulkan-headers/1.3.243.0")
            self.requires("vulkan-loader/1.3.243.0")
        if self.options.with_x11 or self.options.with_xfixes:
            self.requires("xorg/system")

    def validate(self):
        if self.settings.os not in ["FreeBSD", "Linux"]:
            raise ConanInvalidConfiguration(f"{self.name} not supported for {self.settings.os}")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least {self.settings.compiler} version {minimum_version}."
            )
        if os.getenv("CONAN_CENTER_BUILD_SERVICE") is not None and self.options.with_xfixes:
            raise ConanInvalidConfiguration(f"{self.name} requires a newer version of xfixes than is available in CCI")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.0 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = VirtualBuildEnv(self)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

        def feature(option, default=False):
            return "enabled" if self.options.get_safe(option, default=default) else "disabled"

        tc = MesonToolchain(self)
        # Workaround an strict-prototypes error caused by the readline include file: readline/rltypedefs.h
        # todo Report this issue upstream.
        tc.c_args.append("-Wno-error=strict-prototypes")
        # This appears to be an issue that crops up when using Avahi and libpulse involving the malloc_info and malloc_trim functions.
        tc.c_args.append("-Wno-error=implicit-function-declaration")
        for includedir in self.dependencies["linux-headers-generic"].cpp_info.includedirs:
            tc.c_args.append(f"-I{includedir}")
        tc.project_options["alsa"] = feature("with_libalsa")
        tc.project_options["auto_features"] = "disabled"
        tc.project_options["avb"] = "enabled" if self.settings.os == "Linux" else "disabled"
        tc.project_options["avahi"] = feature("with_avahi")
        tc.project_options["compress-offload"] = feature("with_libalsa")
        tc.project_options["datadir"] = "res"
        tc.project_options["dbus"] = feature("with_dbus")
        tc.project_options["docs"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["ffmpeg"] = feature("with_ffmpeg")
        tc.project_options["flatpak"] = feature("flatpak")
        tc.project_options["gsettings"] = feature("gsettings")
        tc.project_options["jack"] = "disabled"
        tc.project_options["legacy-rtkit"] = False
        tc.project_options["libpulse"] = feature("with_pulseaudio")
        tc.project_options["libusb"] = "disabled"
        tc.project_options["man"] = "disabled"
        tc.project_options["pipewire-alsa"] = feature("with_libalsa")
        tc.project_options["pipewire-jack"] = "disabled"
        tc.project_options["pipewire-v4l2"] = "disabled"
        tc.project_options["opus"] = feature("with_opus")
        tc.project_options["pw-cat"] = "enabled"
        tc.project_options["pw-cat-ffmpeg"] = feature("with_ffmpeg")
        tc.project_options["raop"] = feature("raop")
        tc.project_options["readline"] = feature("with_readline")
        tc.project_options["sdl2"] = "disabled"
        tc.project_options["selinux"] = feature("with_selinux")
        tc.project_options["session-managers"] = []
        tc.project_options["sndfile"] = feature("with_libsndfile")
        tc.project_options["spa-plugins"] = "enabled"
        tc.project_options["sysconfdir"] = "res"
        tc.project_options["systemd"] = "disabled"
        tc.project_options["systemd-user-service"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["udev"] = feature("with_libudev", True)
        tc.project_options["udevrulesdir"] = os.path.join("res", "udev", "rules.d")
        tc.project_options["vulkan"] = feature("with_vulkan")
        tc.project_options["x11"] = feature("with_x11")
        tc.project_options["x11-xfixes"] = feature("with_xfixes")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    @property
    def _libpipewire_api_version_txt(self):
        return os.path.join(self.package_folder, "res", "libpipewire-api-version.txt")

    @property
    def _libspa_api_version_txt(self):
        return os.path.join(self.package_folder, "res", "libspa-api-version.txt")

    def package(self):
        copy(
            self,
            "COPYING",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        meson = Meson(self)
        meson.install()

        pkconfig_dir = self.package_path.joinpath("lib", "pkgconfig")
        libpipewire_pc_file = next(pkconfig_dir.glob("libpipewire-*.pc"))
        libspa_pc_file = next(pkconfig_dir.glob("libspa-*.pc"))

        libpipewire_api_version = libpipewire_pc_file.stem.split("-")[1]
        libspa_api_version = libspa_pc_file.stem.split("-")[1]

        save(self, self._libpipewire_api_version_txt, libpipewire_api_version)
        save(self, self._libspa_api_version_txt, libspa_api_version)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        libpipewire_api_version = load(self, self._libpipewire_api_version_txt).strip()
        libspa_api_version = load(self, self._libspa_api_version_txt).strip()

        self.runenv_info.define("PIPEWIRE_CONFIG_DIR", os.path.join(self.package_folder, "res", "pipewire"))
        self.runenv_info.define(
            "PIPEWIRE_MODULE_DIR",
            os.path.join(self.package_folder, "lib", f"pipewire-{libpipewire_api_version}"),
        )
        self.runenv_info.define(
            "SPA_PLUGIN_DIR",
            os.path.join(self.package_folder, "lib", f"libspa-{libspa_api_version}"),
        )
        self.runenv_info.define(
            "SPA_DATA_DIR",
            os.path.join(self.package_folder, "res", f"libspa-{libspa_api_version}"),
        )

        if self.options.with_libalsa:
            self.runenv_info.define(
                "ACP_PATHS_DIR",
                os.path.join(self.package_folder, "res", "alsa-card-profile", "mixer", "paths"),
            )
            self.runenv_info.define(
                "ACP_PROFILES_DIR",
                os.path.join(
                    self.package_folder,
                    "res",
                    "alsa-card-profile",
                    "mixer",
                    "profiles-sets",
                ),
            )
            self.runenv_info.prepend_path("ALSA_PLUGIN_DIR", os.path.join(self.package_folder, "lib", "alsa-lib"))

        self.cpp_info.components["libpipewire"].libs = [f"pipewire-{libpipewire_api_version}"]
        self.cpp_info.components["libpipewire"].includedirs = [
            os.path.join(self.package_folder, "include", f"pipewire-{libpipewire_api_version}")
        ]
        self.cpp_info.components["libpipewire"].defines = ["_REENTRANT"]
        self.cpp_info.components["libpipewire"].set_property(
            "pkg_config_name", f"libpipewire-{libpipewire_api_version}"
        )
        pkgconfig_variables = {
            # todo When Conan V1 doesn't need to be supported, use the ${libdir} variable.
            # 'moduledir': f"${{libdir}}/pipewire-{libpipewire_api_version}",
            "moduledir": f"${{prefix}}/lib/pipewire-{libpipewire_api_version}",
        }
        self.cpp_info.components["libpipewire"].set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()),
        )
        self.cpp_info.components["libpipewire"].requires = ["libspa"]
        if self.options.flatpak:
            self.cpp_info.components["libpipewire"].requires.append("glib::glib-2.0")
        if self.options.gsettings:
            self.cpp_info.components["libpipewire"].requires.append("glib::gio-2.0")
        if self.options.raop:
            self.cpp_info.components["libpipewire"].requires.extend(["openssl::crypto", "openssl::ssl"])
        if self.options.with_avahi:
            self.cpp_info.components["libpipewire"].requires.append("avahi::client")
        if self.options.with_dbus:
            self.cpp_info.components["libpipewire"].requires.append("dbus::dbus")
        if self.options.with_libalsa:
            self.cpp_info.components["libpipewire"].requires.append("libalsa::libalsa")
        if self.options.with_libsndfile:
            self.cpp_info.components["libpipewire"].requires.append("libsndfile::libsndfile")
        if self.options.with_opus:
            self.cpp_info.components["libpipewire"].requires.append("opus::opus")
        if self.options.with_pulseaudio:
            self.cpp_info.components["libpipewire"].requires.append("pulseaudio::pulse")
        if self.options.with_selinux:
            self.cpp_info.components["libpipewire"].requires.append("libselinux::selinux")
        if self.options.with_x11:
            self.cpp_info.components["libpipewire"].requires.append("xorg::x11-xcb")
        if self.options.with_xfixes:
            self.cpp_info.components["libpipewire"].requires.append("xorg::xfixes")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libpipewire"].system_libs.extend(["m", "pthread", "dl"])

        self.cpp_info.components["libspa"].set_property("pkg_config_name", f"libspa-{libspa_api_version}")
        self.cpp_info.components["libspa"].includedirs = [
            os.path.join(self.package_folder, "include", f"spa-{libspa_api_version}")
        ]
        self.cpp_info.components["libspa"].defines = ["_REENTRANT"]
        pkgconfig_variables = {
            # todo When Conan V1 doesn't need to be supported, use the ${libdir} variable.
            # 'plugindir': "${{libdir}}/spa-{libspa_api_version}",
            "plugindir": "${{prefix}}/lib/spa-{libspa_api_version}",
        }
        self.cpp_info.components["libpipewire"].set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()),
        )
        if self.options.with_libalsa:
            self.cpp_info.components["libspa"].requires.append("libalsa::libalsa")
        if self.options.with_dbus:
            self.cpp_info.components["libspa"].requires.append("dbus::dbus")
        if self.options.with_ffmpeg:
            self.cpp_info.components["libspa"].requires.append("ffmpeg::avcodec")
        if self.options.with_libsndfile:
            self.cpp_info.components["libspa"].requires.append("libsndfile::libsndfile")
        if self.options.get_safe("with_libudev", True):
            self.cpp_info.components["libspa"].requires.append("libudev::libudev")
        if self.options.with_vulkan:
            self.cpp_info.components["libspa"].requires.extend(
                [
                    "libdrm::libdrm_libdrm",
                    "linux-headers-generic::linux-headers-generic",
                    "vulkan-headers::vulkan-headers",
                    "vulkan-loader::vulkan-loader",
                ]
            )

        self.cpp_info.components["tools"].requires = ["libpipewire"]

        # pw-cat
        if self.options.with_ffmpeg:
            self.cpp_info.components["tools"].requires.extend(["ffmpeg::avcodec", "ffmpeg::avformat", "ffmpeg::avutil"])
        if self.options.with_libsndfile:
            self.cpp_info.components["tools"].requires.append("libsndfile::libsndfile")

        # pw-top
        if self.options.with_ncurses:
            self.cpp_info.components["tools"].requires.append("ncurses::libcurses")

        # pw-cli
        if self.options.with_readline:
            self.cpp_info.components["tools"].requires.append("readline::readline")

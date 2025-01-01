import os
import shutil
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, rename, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, check_min_vs, is_msvc_static_runtime
from conan.tools.scm import Version

# For PkgConfigDeps.set_property()
required_conan_version = ">=2.8"


class GStPluginsGoodConan(ConanFile):
    name = "gst-plugins-good"
    description = "A set of good-quality plug-ins for GStreamer under GStreamer's preferred license, LGPL"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        "with_asm": [True, False],
        "with_bz2": [True, False],
        "with_cairo": [True, False],
        "with_flac": [True, False],
        "with_gdk_pixbuf": [True, False],
        "with_gtk": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg", False],
        "with_libcaca": [True, False],
        "with_libxml2": [True, False],
        "with_mp3lame": [True, False],
        "with_mpg123": [True, False],
        "with_png": [True, False],
        "with_pulseaudio": [True, False],
        "with_qt": [True, False],
        "with_soup": [True, False],
        "with_ssl": ["openssl", False],
        "with_taglib": [True, False],
        "with_vpx": [True, False],

        "with_egl": [True, False],
        "with_v4l2": [True, False],
        "with_wayland": [True, False],
        "with_xorg": [True, False],

        "with_directsound": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,

        "with_asm": True,
        "with_bz2": True,
        "with_cairo": True,
        "with_flac": True,
        "with_gdk_pixbuf": True,
        "with_gtk": True,
        "with_jpeg": "libjpeg",
        "with_libcaca": True,
        "with_libxml2": True,
        "with_mp3lame": True,
        "with_mpg123": True,
        "with_png": True,
        "with_pulseaudio": True,
        "with_qt": True,
        "with_soup": True,
        "with_ssl": "openssl",
        "with_taglib": True,
        "with_vpx": True,

        "with_egl": True,
        "with_v4l2": True,
        "with_wayland": True,
        "with_xorg": True,

        "with_directsound": True,
    }
    languages = ["C"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_directsound
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_egl
            del self.options.with_v4l2
            del self.options.with_wayland
            del self.options.with_xorg
        if self.settings.arch != "x86_64":
            del self.options.with_asm

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.with_qt and self.settings.os in ["Linux", "FreeBSD"]:
            self.options["gst-plugins-base"].with_egl = self.options.with_egl
            self.options["gst-plugins-base"].with_xorg = self.options.with_xorg
            self.options["gst-plugins-base"].with_wayland = self.options.with_wayland
        else:
            self.options.rm_safe("with_wayland")
            self.options.rm_safe("with_egl")
        self.options["gstreamer"].shared = self.options.shared
        self.options["gst-plugins-base"].shared = self.options.shared

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _qt_options(self):
        opts = {}
        opts["qtdeclarative"] = True
        opts["qtshadertools"] = True
        if self.settings.os in ["Linux", "FreeBSD"]:
            opts["with_x11"] = self.options.with_xorg
            opts["with_egl"] = self.options.with_egl
            opts["qtwayland"] = self.options.with_wayland
        return opts

    def requirements(self):
        self.requires(f"gstreamer/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires(f"gst-plugins-base/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("gst-orc/0.4.40")

        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_cairo:
            self.requires("cairo/1.18.0")
        if self.options.with_flac:
            self.requires("flac/1.4.2")
        if self.options.with_gdk_pixbuf:
            self.requires("gdk-pixbuf/2.42.10")
        if self.options.with_gtk:
            # Only GTK 3 is supported
            self.requires("gtk/3.24.43")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.4")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.with_libcaca:
            self.requires("libcaca/0.99.beta20")
        if self.options.with_libxml2:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.with_mp3lame:
            self.requires("libmp3lame/3.100")
        if self.options.with_mpg123:
            self.requires("mpg123/1.31.2")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_pulseaudio:
            self.requires("pulseaudio/17.0")
        if self.options.with_qt:
            self.requires("qt/[>=6.7 <7]", options={
                **self._qt_options,
                "qttools": can_run(self)
            })
        if self.options.with_soup:
            self.requires("libsoup/3.6.1")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_taglib:
            self.requires("taglib/2.0")
        if self.options.get_safe("with_v4l2"):
            self.requires("libv4l/1.28.1")
        if self.options.with_vpx:
            self.requires("libvpx/1.14.1")
        if self.options.get_safe("with_xorg"):
            self.requires("xorg/system")

    def validate(self):
        if (self.options.shared != self.dependencies["gstreamer"].options.shared or
            self.options.shared != self.dependencies["glib"].options.shared or
            self.options.shared != self.dependencies["gst-plugins-base"].options.shared):
                # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
                raise ConanInvalidConfiguration("GLib, GStreamer and GstPlugins must be either all shared, or all static")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"gst-plugins-good {self.version} does not support gcc older than 5")
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared build with static runtime is not supported due to the FlsAlloc limit")
        if self.options.with_qt and not self.dependencies["gst-plugins-base"].options.with_gl:
            raise ConanInvalidConfiguration("-o with_qt=True requires -o gst-plugins-base/*:with_gl=True")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("gst-orc/<host_version>")
        self.tool_requires("gettext/0.22.5")
        if self.options.get_safe("with_asm"):
            self.tool_requires("nasm/2.16.01")
        if self.options.with_qt and not can_run(self):
            self.tool_requires("qt/<host_version>", options={
                **self._qt_options,
                "qttools": True
            })

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if self.options.with_qt and can_run(self):
            # Required for host-context Qt tools with shared deps
            VirtualRunEnv(self).generate(scope="build")

        tc = MesonToolchain(self)

        if is_msvc(self) and not check_min_vs(self, 190, raise_invalid=False):
            tc.c_link_args.append("-Dsnprintf=_snprintf")

        def feature(value):
            return "enabled" if value else "disabled"

        # Feature options for plugins without external deps
        tc.project_options["alpha"] = "enabled"
        tc.project_options["apetag"] = "enabled"
        tc.project_options["audiofx"] = "enabled"
        tc.project_options["audioparsers"] = "enabled"
        tc.project_options["auparse"] = "enabled"
        tc.project_options["autodetect"] = "enabled"
        tc.project_options["avi"] = "enabled"
        tc.project_options["cutter"] = "enabled"
        tc.project_options["debugutils"] = "enabled"
        tc.project_options["deinterlace"] = "enabled"
        tc.project_options["dtmf"] = "enabled"
        tc.project_options["effectv"] = "enabled"
        tc.project_options["equalizer"] = "enabled"
        tc.project_options["flv"] = "enabled"
        tc.project_options["flx"] = "enabled"
        tc.project_options["goom"] = "enabled"
        tc.project_options["goom2k1"] = "enabled"
        tc.project_options["icydemux"] = "enabled"
        tc.project_options["id3demux"] = "enabled"
        tc.project_options["imagefreeze"] = "enabled"
        tc.project_options["interleave"] = "enabled"
        tc.project_options["isomp4"] = "enabled"
        tc.project_options["law"] = "enabled"
        tc.project_options["level"] = "enabled"
        tc.project_options["matroska"] = "enabled"
        tc.project_options["monoscope"] = "enabled"
        tc.project_options["multifile"] = "enabled"
        tc.project_options["multipart"] = "enabled"
        tc.project_options["replaygain"] = "enabled"
        tc.project_options["rtp"] = "enabled"
        tc.project_options["rtpmanager"] = "enabled"
        tc.project_options["rtsp"] = "enabled"
        tc.project_options["shapewipe"] = "enabled"
        tc.project_options["smpte"] = "enabled"
        tc.project_options["spectrum"] = "enabled"
        tc.project_options["udp"] = "enabled"
        tc.project_options["videobox"] = "enabled"
        tc.project_options["videocrop"] = "enabled"
        tc.project_options["videofilter"] = "enabled"
        tc.project_options["videomixer"] = "enabled"
        tc.project_options["wavenc"] = "enabled"
        tc.project_options["wavparse"] = "enabled"
        tc.project_options["xingmux"] = "enabled"
        tc.project_options["y4m"] = "enabled"

        # Feature options for plugins with external deps
        tc.project_options["aalib"] = "disabled"  # TODO: libaa1
        tc.project_options["adaptivedemux2"] = feature(self.options.with_ssl and self.options.with_libxml2 and self.options.with_soup)
        tc.project_options["amrnb"] = "disabled"  # TODO: libopencore-amrnb
        tc.project_options["amrwbdec"] = "disabled"  # TODO: libopencore-amrwbdec
        tc.project_options["bz2"] = feature(self.options.with_bz2)
        tc.project_options["cairo"] = feature(self.options.with_cairo)
        tc.project_options["directsound"] = feature(self.options.get_safe("with_directsound"))
        tc.project_options["dv"] = "disabled"  # TODO: libdv4
        tc.project_options["dv1394"] = "disabled"  # TODO: libraw1394, libavc1394, libiec61883
        tc.project_options["flac"] = feature(self.options.with_flac)
        tc.project_options["gdk-pixbuf"] = feature(self.options.with_gdk_pixbuf)
        tc.project_options["gtk3"] = feature(self.options.with_gtk)
        tc.project_options["jack"] = "enabled"  # requires libjack, but only via dlopen
        tc.project_options["jpeg"] = feature(self.options.with_jpeg)
        tc.project_options["lame"] = feature(self.options.with_mp3lame)
        tc.project_options["libcaca"] = feature(self.options.with_libcaca)
        tc.project_options["mpg123"] = feature(self.options.with_mpg123)
        tc.project_options["oss"] = feature(self.settings.os in ["Linux", "FreeBSD"])
        tc.project_options["oss4"] = feature(self.settings.os in ["Linux", "FreeBSD"])
        tc.project_options["osxaudio"] = feature(is_apple_os(self))
        tc.project_options["osxvideo"] = feature(self.settings.os == "Macos")
        tc.project_options["png"] = feature(self.options.with_png)
        tc.project_options["pulse"] = feature(self.options.with_pulseaudio)
        tc.project_options["rpicamsrc"] = "disabled" # Raspberry Pi camera module plugin
        tc.project_options["shout2"] = "disabled"  # TODO: libshout
        tc.project_options["soup"] = feature(self.options.with_soup)
        tc.project_options["speex"] = "disabled"  # TODO: libspeex
        tc.project_options["taglib"] = feature(self.options.with_taglib)
        tc.project_options["twolame"] = "disabled"  # TODO: libtwolame
        tc.project_options["v4l2"] = feature(self.options.get_safe("with_v4l2"))
        tc.project_options["vpx"] = feature(self.options.get_safe("with_vpx"))
        tc.project_options["waveform"] = feature(self.settings.os == "Windows")
        tc.project_options["wavpack"] = "disabled"  # TODO: libwavpack

        # HLS plugin options
        tc.project_options["hls-crypto"] = "openssl"

        # Qt plugin options
        tc.project_options["qt-method"] = "pkg-config"
        tc.project_options["qt5"] = feature(self.options.with_qt and Version(self.dependencies["qt"].ref.version).major == 5)
        tc.project_options["qt6"] = feature(self.options.with_qt and Version(self.dependencies["qt"].ref.version).major == 6)
        tc.project_options["qt-egl"] = feature(self.options.get_safe("with_egl"))
        tc.project_options["qt-wayland"] = feature(self.options.get_safe("with_wayland"))
        tc.project_options["qt-x11"] = feature(self.options.get_safe("with_xorg"))

        # ximagesrc plugin options
        tc.project_options["ximagesrc"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["ximagesrc-xshm"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["ximagesrc-xfixes"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["ximagesrc-xdamage"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["ximagesrc-navigation"] = feature(self.options.get_safe("with_xorg"))

        # Common feature options
        tc.project_options["doc"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["nls"] = "enabled"
        tc.project_options["orc"] = "enabled"
        tc.project_options["asm"] = feature(self.options.get_safe("with_asm"))

        if not self.dependencies["gst-orc"].options.shared:
            # The define is not propagated correctly in the Meson build scripts
            tc.extra_defines.append("ORC_STATIC_COMPILATION")

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.set_property("libmp3lame", "pkg_config_name", "mp3lame")
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        if is_msvc(self):
            for filename_old in Path(path).glob("*.a"):
                filename_new = str(filename_old)[:-2] + ".lib"
                shutil.move(filename_old, filename_new)

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "gstreamer-1.0", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        if self.options.shared:
            self.runenv_info.append_path("GST_PLUGIN_PATH", os.path.join(self.package_folder, "lib", "gstreamer-1.0"))

        def _define_plugin(name, extra_requires):
            name = f"gst{name}"
            component = self.cpp_info.components[name]
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
                "glib::gobject-2.0",
                "glib::glib-2.0",
            ] + extra_requires
            component.includedirs = []
            component.bindirs = []
            component.resdirs = ["res"]
            if self.options.shared:
                component.bindirs.append(os.path.join("lib", "gstreamer-1.0"))
            else:
                component.libs = [name]
                component.libdirs = [os.path.join("lib", "gstreamer-1.0")]
                if self.settings.os in ["Linux", "FreeBSD"]:
                    component.system_libs = ["m", "dl"]
                component.defines.append("GST_PLUGINS_GOOD_STATIC")
            return component

        # adaptivedemux2
        if self.options.with_ssl and self.options.with_libxml2 and self.options.with_soup:
            _define_plugin("adaptivedemux2", [
                "gst-plugins-base::gstreamer-tag-1.0",
                "gstreamer::gstreamer-net-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-app-1.0",
                "libxml2::libxml2",
                "openssl::crypto",
                "libsoup::libsoup",
                "glib::gmodule-2.0",
                "glib::gio-2.0",
            ])
        # alaw
        _define_plugin("alaw", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # alpha
        _define_plugin("alpha", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # alphacolor
        _define_plugin("alphacolor", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # apetag
        _define_plugin("apetag", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
        ])
        # audiofx
        _define_plugin("audiofx", [
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-fft-1.0",
            "gst-orc::gst-orc",
        ])
        # audioparsers
        _define_plugin("audioparsers", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
        ])
        # auparse
        _define_plugin("auparse", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # autodetect
        _define_plugin("autodetect", [])
        # avi
        _define_plugin("avi", [
            "gst-plugins-base::gstreamer-riff-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
        ])
        # cacasink
        if self.options.with_libcaca:
            _define_plugin("cacasink", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libcaca::libcaca",
            ])
        # cairo
        if self.options.with_cairo:
            _define_plugin("cairo", [
                "gst-plugins-base::gstreamer-video-1.0",
                "cairo::cairo-gobject",
            ])
        # cutter
        _define_plugin("cutter", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # debug
        _define_plugin("debug", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # deinterlace
        _define_plugin("deinterlace", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-orc::gst-orc",
        ])
        # directsound
        if self.options.get_safe("with_directsound"):
            gst_ds = _define_plugin("directsound", [
                "gst-plugins-base::gstreamer-audio-1.0",
            ])
            gst_ds.system_libs = ["dsound", "winmm", "ole32"]
        # dtmf
        _define_plugin("dtmf", [
            "gst-plugins-base::gstreamer-rtp-1.0",
        ])
        # effectv
        _define_plugin("effectv", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # equalizer
        _define_plugin("equalizer", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # flac
        if self.options.with_flac:
            _define_plugin("flac", [
                "gst-plugins-base::gstreamer-tag-1.0",
                "gst-plugins-base::gstreamer-audio-1.0",
                "flac::flac",
            ])
        # flv
        _define_plugin("flv", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # flxdec
        _define_plugin("flxdec", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # gdkpixbuf
        if self.options.with_gdk_pixbuf:
            _define_plugin("gdkpixbuf", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer::gstreamer-controller-1.0",
                "gdk-pixbuf::gdk-pixbuf",
            ])
        # goom
        _define_plugin("goom", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-orc::gst-orc",
        ])
        # goom2k1
        _define_plugin("goom2k1", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        # gtk
        if self.options.with_gtk:
            _define_plugin("gtk", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gtk::gtk+-3.0",
            ])
        # icydemux
        _define_plugin("icydemux", [
            "gst-plugins-base::gstreamer-tag-1.0",
            "zlib::zlib",
        ])
        # id3demux
        _define_plugin("id3demux", [
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        # imagefreeze
        _define_plugin("imagefreeze", [])
        # interleave
        _define_plugin("interleave", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # isomp4
        _define_plugin("isomp4", [
            "gst-plugins-base::gstreamer-riff-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-rtp-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "zlib::zlib",
        ])
        # jack
        _define_plugin("jack", [
            "gst-plugins-base::gstreamer-audio-1.0",
            "glib::gmodule-2.0",
        ])
        # jpeg
        _define_plugin("jpeg", [
            "gst-plugins-base::gstreamer-video-1.0",
            "libjpeg::libjpeg",
        ])
        # lame
        _define_plugin("lame", [
            "gst-plugins-base::gstreamer-audio-1.0",
            "libmp3lame::libmp3lame",
        ])
        # level
        _define_plugin("level", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # matroska
        if self.options.with_bz2:
            _define_plugin("matroska", [
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-audio-1.0",
                "gst-plugins-base::gstreamer-riff-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-tag-1.0",
                "zlib::zlib",
                "bzip2::bzip2",
            ])
        # monoscope
        _define_plugin("monoscope", [
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # mpg123
        if self.options.with_mpg123:
            _define_plugin("mpg123", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "mpg123::mpg123",
            ])
        # mulaw
        _define_plugin("mulaw", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # multifile
        _define_plugin("multifile", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "glib::gio-2.0",
        ])
        # multipart
        _define_plugin("multipart", [])
        # navigationtest
        _define_plugin("navigationtest", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # oss4
        if self.settings.os == "Linux":
            _define_plugin("oss4", [
                "gst-plugins-base::gstreamer-audio-1.0",
            ])
        # ossaudio
        if self.settings.os == "Linux":
            _define_plugin("ossaudio", [
                "gst-plugins-base::gstreamer-audio-1.0",
            ])
        # osxaudio
        if is_apple_os(self):
            gst_osxaudio = _define_plugin("osxaudio", [
                "gst-plugins-base::gstreamer-audio-1.0",
            ])
            gst_osxaudio.frameworks = ["CoreAudio", "AudioToolbox"]
            if self.settings.os == "Macos":
                gst_osxaudio.frameworks.extend(["AudioUnit", "CoreServices"])
        # osxvideo
        if self.settings.os == "Macos":
            gst_osxvideo = _define_plugin("osxvideo", [
                "gst-plugins-base::gstreamer-video-1.0",
            ])
            gst_osxvideo.frameworks = ["OpenGL", "Cocoa"]
        # png
        if self.options.with_png:
            _define_plugin("png", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libpng::libpng",
            ])
        # pulseaudio
        if self.options.with_pulseaudio:
            _define_plugin("pulseaudio", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "pulseaudio::pulseaudio",
            ])
        # qml6
        if self.options.with_qt:
            qt_major = Version(self.dependencies["qt"].ref.version).major
            qt_plugin = _define_plugin("qml6" if qt_major == 6 else "qmlgl", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-gl-1.0",
                "gst-plugins-base::gstreamer-gl-prototypes-1.0",
                "qt::qtCore",
                "qt::qtGui",
                "qt::qtQml",
                "qt::qtQuick",
            ])
            if self.options.get_safe("with_xorg"):
                qt_plugin.requires.append("gst-plugins-base::gstreamer-gl-x11-1.0")
            if self.options.get_safe("with_wayland"):
                qt_plugin.requires.append("gst-plugins-base::gstreamer-gl-wayland-1.0")
                qt_plugin.requires.append("qt::qtWaylandClient")
            if self.options.get_safe("with_egl"):
                qt_plugin.requires.append("gst-plugins-base::gstreamer-gl-egl-1.0")
            if self.settings.os == "Windows":
                qt_plugin.system_libs.append("opengl32")
            if qt_major == 5:
                if self.options.get_safe("with_xorg"):
                    qt_plugin.requires.append("qt::qtX11Extras")
                if self.settings.os == "Android":
                    qt_plugin.requires.append("qt::qtAndroidExtras")
                    qt_plugin.system_libs.append("GLESv2")
                if is_apple_os(self):
                    qt_plugin.requires.append("qt::qtMacExtras")
        # replaygain
        _define_plugin("replaygain", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # rtp
        _define_plugin("rtp", [
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-rtp-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        # rtpmanager
        _define_plugin("rtpmanager", [
            "gstreamer::gstreamer-net-1.0",
            "gst-plugins-base::gstreamer-rtp-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "glib::gio-2.0",
        ])
        # rtsp
        _define_plugin("rtsp", [
            "gst-plugins-base::gstreamer-rtp-1.0",
            "gst-plugins-base::gstreamer-rtsp-1.0",
            "gst-plugins-base::gstreamer-sdp-1.0",
            "gstreamer::gstreamer-net-1.0",
            "glib::gio-2.0",
        ])
        # shapewipe
        _define_plugin("shapewipe", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # smpte
        _define_plugin("smpte", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # soup
        if self.options.with_soup:
            _define_plugin("soup", [
                "gst-plugins-base::gstreamer-tag-1.0",
                "libsoup::libsoup",
                "glib::gmodule-2.0",
                "glib::gio-2.0",
            ])
        # spectrum
        _define_plugin("spectrum", [
            "gst-plugins-base::gstreamer-fft-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # taglib
        if self.options.with_taglib:
            _define_plugin("taglib", [
                "gst-plugins-base::gstreamer-tag-1.0",
                "taglib::taglib",
            ])
        # udp
        _define_plugin("udp", [
            "gstreamer::gstreamer-net-1.0",
            "glib::gio-2.0",
        ])
        # video4linux2
        if self.options.get_safe("with_v4l2"):
            _define_plugin("video4linux2", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "libv4l::libv4l",
            ])
        # videobox
        _define_plugin("videobox", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-orc::gst-orc",
        ])
        # videocrop
        _define_plugin("videocrop", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # videofilter
        _define_plugin("videofilter", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # videomixer
        _define_plugin("videomixer", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-orc::gst-orc",
        ])
        # vpx
        if self.options.with_vpx:
            _define_plugin("vpx", [
                "gst-plugins-base::gstreamer-tag-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "libvpx::libvpx",
            ])
        # waveform
        if self.settings.os == "Windows":
            gst_wf = _define_plugin("waveform", [
                "gst-plugins-base::gstreamer-audio-1.0",
            ])
            gst_wf.system_libs = ["winmm"]
        # wavenc
        _define_plugin("wavenc", [
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-riff-1.0",
        ])
        # wavparse
        _define_plugin("wavparse", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-riff-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
        ])
        # ximagesrc
        if self.options.get_safe("with_xorg"):
            _define_plugin("ximagesrc", [
                "gst-plugins-base::gstreamer-video-1.0",
                "xorg::x11",
                "xorg::xext",
                "xorg::xfixes",
                "xorg::xdamage",
                "xorg::xtst",
            ])
        # xingmux
        _define_plugin("xingmux", [])
        # y4menc
        _define_plugin("y4menc", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])

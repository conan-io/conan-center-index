import os
import re
import shutil
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
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

def _get_option(plugin):
    return {
        "alaw": "law",
        "alphacolor": "alpha",
        "cacasink": "libcaca",
        "debug": "debugutils",
        "flxdec": "flx",
        "gdkpixbuf": "gdk-pixbuf",
        "gtk": "gtk3",
        "mulaw": "law",
        "navigationtest": "debugutils",
        "ossaudio": "oss",
        "pulseaudio": "pulse",
        "qml6": "qt6",
        "qmlgl": "qt5",
        "video4linux2": "v4l2",
        "y4menc": "y4m",
    }.get(plugin, plugin)

class GStPluginsGoodConan(ConanFile):
    name = "gst-plugins-good"
    description = "A set of good-quality plug-ins for GStreamer under GStreamer's preferred license, LGPL"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"

    _plugins = {
        "adaptivedemux2": [
            "gstreamer-tag-1.0",
            "gstreamer-net-1.0",
            "gstreamer-pbutils-1.0",
            "gstreamer-app-1.0",
            "libxml2::libxml2",
            "openssl::crypto",
            "libsoup::libsoup",
            "glib::gmodule-2.0",
            "glib::gio-2.0",
        ],
        "alaw": [
            "gstreamer-audio-1.0",
        ],
        "alpha": [
            "gstreamer-video-1.0",
        ],
        "alphacolor": [
            "gstreamer-video-1.0",
        ],
        "apetag": [
            "gstreamer-pbutils-1.0",
            "gstreamer-tag-1.0",
        ],
        "audiofx": [
            "gstreamer-audio-1.0",
            "gstreamer-fft-1.0",
            "gst-orc::gst-orc",
        ],
        "audioparsers": [
            "gstreamer-pbutils-1.0",
            "gstreamer-audio-1.0",
            "gstreamer-tag-1.0",
        ],
        "auparse": [
            "gstreamer-audio-1.0",
        ],
        "autodetect": [],
        "avi": [
            "gstreamer-riff-1.0",
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
            "gstreamer-tag-1.0",
        ],
        "cacasink": [
            "gstreamer-video-1.0",
            "libcaca::libcaca",
        ],
        "cairo": [
            "gstreamer-video-1.0",
            "cairo::cairo-gobject",
        ],
        "cutter": [
            "gstreamer-audio-1.0",
        ],
        "debug": [
            "gstreamer-video-1.0",
        ],
        "deinterlace": [
            "gstreamer-video-1.0",
            "gst-orc::gst-orc",
        ],
        "directsound": [
            "gstreamer-audio-1.0",
        ],
        "dtmf": [
            "gstreamer-rtp-1.0",
        ],
        "effectv": [
            "gstreamer-video-1.0",
        ],
        "equalizer": [
            "gstreamer-audio-1.0",
        ],
        "flac": [
            "gstreamer-tag-1.0",
            "gstreamer-audio-1.0",
            "flac::flac",
        ],
        "flv": [
            "gstreamer-pbutils-1.0",
            "gstreamer-video-1.0",
            "gstreamer-tag-1.0",
            "gstreamer-audio-1.0",
        ],
        "flxdec": [
            "gstreamer-video-1.0",
        ],
        "gdkpixbuf": [
            "gstreamer-video-1.0",
            "gstreamer-controller-1.0",
            "gdk-pixbuf::gdk-pixbuf",
        ],
        "goom": [
            "gstreamer-pbutils-1.0",
            "gst-orc::gst-orc",
        ],
        "goom2k1": [
            "gstreamer-pbutils-1.0",
        ],
        "gtk": [
            "gstreamer-video-1.0",
            "gtk::gtk+-3.0",
            "opengl::opengl"
        ],
        "icydemux": [
            "gstreamer-tag-1.0",
            "zlib::zlib",
        ],
        "id3demux": [
            "gstreamer-tag-1.0",
            "gstreamer-pbutils-1.0",
        ],
        "imagefreeze": [],
        "interleave": [
            "gstreamer-audio-1.0",
        ],
        "isomp4": [
            "gstreamer-riff-1.0",
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
            "gstreamer-rtp-1.0",
            "gstreamer-tag-1.0",
            "gstreamer-pbutils-1.0",
            "zlib::zlib",
        ],
        "jack": [
            "gstreamer-audio-1.0",
            "glib::gmodule-2.0",
        ],
        "jpeg": [
            "gstreamer-video-1.0",
            "libjpeg::libjpeg",
        ],
        "lame": [
            "gstreamer-audio-1.0",
            "libmp3lame::libmp3lame",
        ],
        "level": [
            "gstreamer-audio-1.0",
        ],
        "matroska": [
            "gstreamer-pbutils-1.0",
            "gstreamer-audio-1.0",
            "gstreamer-riff-1.0",
            "gstreamer-video-1.0",
            "gstreamer-tag-1.0",
            "zlib::zlib",
            "bzip2::bzip2",
        ],
        "monoscope": [
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
        ],
        "mpg123": [
            "gstreamer-audio-1.0",
            "mpg123::mpg123",
        ],
        "mulaw": [
            "gstreamer-audio-1.0",
        ],
        "multifile": [
            "gstreamer-video-1.0",
            "gstreamer-pbutils-1.0",
            "glib::gio-2.0",
        ],
        "multipart": [],
        "navigationtest": [
            "gstreamer-video-1.0",
        ],
        "oss4": [
            "gstreamer-audio-1.0",
        ],
        "ossaudio": [
            "gstreamer-audio-1.0",
        ],
        "osxaudio": [
            "gstreamer-audio-1.0",
        ],
        "osxvideo": [
            "gstreamer-video-1.0",
        ],
        "png": [
            "gstreamer-video-1.0",
            "libpng::libpng",
        ],
        "pulseaudio": [
            "gstreamer-audio-1.0",
            "gstreamer-pbutils-1.0",
            "pulseaudio::pulseaudio",
        ],
        "qmlgl": [
            "gstreamer-video-1.0",
            "gstreamer-gl-1.0",
            "gstreamer-gl-prototypes-1.0",
            "qt::qtCore",
            "qt::qtGui",
            "qt::qtQml",
            "qt::qtQuick",
        ],
        "qml6": [
            "gstreamer-video-1.0",
            "gstreamer-gl-1.0",
            "gstreamer-gl-prototypes-1.0",
            "qt::qtCore",
            "qt::qtGui",
            "qt::qtQml",
            "qt::qtQuick",
        ],
        "replaygain": [
            "gstreamer-pbutils-1.0",
            "gstreamer-audio-1.0",
        ],
        "rtp": [
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
            "gstreamer-tag-1.0",
            "gstreamer-rtp-1.0",
            "gstreamer-pbutils-1.0",
        ],
        "rtpmanager": [
            "gstreamer-net-1.0",
            "gstreamer-rtp-1.0",
            "gstreamer-audio-1.0",
            "glib::gio-2.0",
        ],
        "rtsp": [
            "gstreamer-rtp-1.0",
            "gstreamer-rtsp-1.0",
            "gstreamer-sdp-1.0",
            "gstreamer-net-1.0",
            "glib::gio-2.0",
        ],
        "shapewipe": [
            "gstreamer-video-1.0",
        ],
        "smpte": [
            "gstreamer-video-1.0",
        ],
        "soup": [
            "gstreamer-tag-1.0",
            "libsoup::libsoup",
            "glib::gmodule-2.0",
            "glib::gio-2.0",
        ],
        "spectrum": [
            "gstreamer-fft-1.0",
            "gstreamer-audio-1.0",
        ],
        "taglib": [
            "gstreamer-tag-1.0",
            "taglib::taglib",
        ],
        "udp": [
            "gstreamer-net-1.0",
            "glib::gio-2.0",
        ],
        "video4linux2": [
            "gstreamer-video-1.0",
            "gstreamer-allocators-1.0",
            "libv4l::libv4l",
        ],
        "videobox": [
            "gstreamer-video-1.0",
            "gst-orc::gst-orc",
        ],
        "videocrop": [
            "gstreamer-video-1.0",
        ],
        "videofilter": [
            "gstreamer-video-1.0",
        ],
        "videomixer": [
            "gstreamer-video-1.0",
            "gst-orc::gst-orc",
        ],
        "vpx": [
            "gstreamer-tag-1.0",
            "gstreamer-video-1.0",
            "libvpx::libvpx",
        ],
        "waveform": [
            "gstreamer-audio-1.0",
        ],
        "wavenc": [
            "gstreamer-audio-1.0",
            "gstreamer-riff-1.0",
        ],
        "wavparse": [
            "gstreamer-pbutils-1.0",
            "gstreamer-riff-1.0",
            "gstreamer-audio-1.0",
            "gstreamer-tag-1.0",
        ],
        "ximagesrc": [
            "gstreamer-video-1.0",
            "xorg::x11",
            "xorg::xext",
            "xorg::xfixes",
            "xorg::xdamage",
            "xorg::xtst",
        ],
        "xingmux": [],
        "y4menc": [
            "gstreamer-video-1.0",
        ],
    }

    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        "with_asm": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg", False],
        "with_egl": [True, False],
        "with_wayland": [True, False],
        "with_xorg": [True, False],

        **{_get_option(plugin): [True, False] for plugin in _plugins},
    }
    default_options = {
        "shared": False,
        "fPIC": True,

        "with_asm": True,
        "with_jpeg": "libjpeg",
        "with_egl": True,
        "with_wayland": True,
        "with_xorg": True,

        **{_get_option(plugin): True for plugin in _plugins},
    }
    languages = ["C"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.pulse
        else:
            del self.options.directsound
            del self.options.waveform
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.ximagesrc
            del self.options.v4l2
            del self.options.with_egl
            del self.options.with_wayland
            del self.options.with_xorg
        if self.settings.os != "Macos":
            del self.options.osxaudio
            del self.options.osxvideo
        if self.settings.arch != "x86_64":
            del self.options.with_asm
        self.options.qt5 = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self._with_qt and self.settings.os in ["Linux", "FreeBSD"]:
            self.options["gst-plugins-base"].with_gl = True
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

    def _is_enabled(self, plugin):
        return self.options.get_safe(_get_option(plugin), False)

    def _reqs(self, plugin):
        reqs = []
        for req in self._plugins[plugin]:
            m = re.fullmatch("gstreamer-(.+)-1.0", req)
            if m:
                if m[1] in _gstreamer_libs:
                    reqs.append(f"gstreamer::{m[1]}")
                elif m[1] in _plugins_base_libs:
                    reqs.append(f"gst-plugins-base::{m[1]}")
                else:
                    raise ConanException(f"Unknown GStreamer library: {req}")
            else:
                reqs.append(req)
        return reqs

    @property
    def _plugin_reqs(self):
        requires = set()
        for plugin in self._plugins:
            if self._is_enabled(plugin):
                requires.update({req.split("::")[0] for req in self._reqs(plugin)})
        return requires

    @property
    def _with_qt(self):
        return self.options.qt5 or self.options.qt6

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
        reqs = self._plugin_reqs
        self.requires(f"gstreamer/{self.version}", transitive_headers=True, transitive_libs=True)
        if "gst-plugins-base" in reqs:
            self.requires(f"gst-plugins-base/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("gst-orc/0.4.40")

        if "zlib" in reqs:
            self.requires("zlib/[>=1.2.11 <2]")
        if "bzip2" in reqs:
            self.requires("bzip2/1.0.8")
        if "cairo" in reqs:
            self.requires("cairo/1.18.0")
        if "flac" in reqs:
            self.requires("flac/1.4.2")
        if "gdk-pixbuf" in reqs:
            self.requires("gdk-pixbuf/2.42.10")
        if "gtk" in reqs:
            # Only GTK 3 is supported
            self.requires("gtk/3.24.43")
        if "libjpeg" in reqs:
            if self.options.with_jpeg == "libjpeg":
                self.requires("libjpeg/9e")
            elif self.options.with_jpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.0.4")
            elif self.options.with_jpeg == "mozjpeg":
                self.requires("mozjpeg/4.1.5")
        if "libcaca" in reqs:
            self.requires("libcaca/0.99.beta20")
        if "libxml2" in reqs:
            self.requires("libxml2/[>=2.12.5 <3]")
        if "libmp3lame" in reqs:
            self.requires("libmp3lame/3.100")
        if "mpg123" in reqs:
            self.requires("mpg123/1.31.2")
        if "libpng" in reqs:
            self.requires("libpng/[>=1.6 <2]")
        if "opengl" in reqs:
            self.requires("opengl/system")
        if "pulseaudio" in reqs:
            self.requires("pulseaudio/17.0")
        if "qt" in reqs:
            ref = "qt/[>=6.7 <7]" if self.options.qt6 else "qt/[~5.15]"
            self.requires(ref, options={
                **self._qt_options,
                "qttools": can_run(self)
            })
        if "libsoup" in reqs:
            self.requires("libsoup/3.6.1")
        if "openssl" in reqs:
            self.requires("openssl/[>=1.1 <4]")
        if "taglib" in reqs:
            self.requires("taglib/2.0")
        if "libv4l" in reqs:
            self.requires("libv4l/1.28.1")
        if "libvpx" in reqs:
            self.requires("libvpx/1.14.1")
        if "xorg" in reqs:
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
        if self.options.qt5 and self.options.qt6:
            raise ConanInvalidConfiguration("Only one of with_qt=True and with_qt6=True can be enabled")
        if self._with_qt and not self.dependencies["gst-plugins-base"].options.with_gl:
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
        if self._with_qt and not can_run(self):
            self.tool_requires("qt/<host_version>", options={
                **self._qt_options,
                "qttools": True
            })

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if self._with_qt and can_run(self):
            # Required for host-context Qt tools with shared deps
            VirtualRunEnv(self).generate(scope="build")

        tc = MesonToolchain(self)

        if is_msvc(self) and not check_min_vs(self, 190, raise_invalid=False):
            tc.c_link_args.append("-Dsnprintf=_snprintf")

        def feature(value):
            return "enabled" if value else "disabled"

        for plugin in self._plugins:
            tc.project_options[_get_option(plugin)] = feature(self._is_enabled(plugin))

        # Feature options for plugins with external deps
        tc.project_options["aalib"] = "disabled"  # TODO: libaa1
        tc.project_options["amrnb"] = "disabled"  # TODO: libopencore-amrnb
        tc.project_options["amrwbdec"] = "disabled"  # TODO: libopencore-amrwbdec
        tc.project_options["dv"] = "disabled"  # TODO: libdv4
        tc.project_options["dv1394"] = "disabled"  # TODO: libraw1394, libavc1394, libiec61883
        tc.project_options["jack"] = "enabled"  # requires libjack, but only via dlopen
        tc.project_options["rpicamsrc"] = "disabled" # Raspberry Pi camera module plugin
        tc.project_options["shout2"] = "disabled"  # TODO: libshout
        tc.project_options["speex"] = "disabled"  # TODO: libspeex
        tc.project_options["twolame"] = "disabled"  # TODO: libtwolame
        tc.project_options["wavpack"] = "disabled"  # TODO: libwavpack

        # HLS plugin options
        tc.project_options["hls-crypto"] = "openssl"

        # Qt plugin options
        tc.project_options["qt-method"] = "pkg-config"
        tc.project_options["qt-egl"] = feature(self.options.get_safe("with_egl"))
        tc.project_options["qt-wayland"] = feature(self.options.get_safe("with_wayland"))
        tc.project_options["qt-x11"] = feature(self.options.get_safe("with_xorg"))

        # ximagesrc plugin options
        tc.project_options["ximagesrc-xshm"] = feature(self.options.get_safe("ximagesrc"))
        tc.project_options["ximagesrc-xfixes"] = feature(self.options.get_safe("ximagesrc"))
        tc.project_options["ximagesrc-xdamage"] = feature(self.options.get_safe("ximagesrc"))
        tc.project_options["ximagesrc-navigation"] = feature(self.options.get_safe("ximagesrc"))

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

        for plugin in self._plugins:
            if self._is_enabled(plugin):
                _define_plugin(plugin, self._reqs(plugin))

        # directsound
        if self.options.get_safe("directsound"):
            gst_directsound = self.cpp_info.components["gstdirectsound"]
            gst_directsound.system_libs = ["dsound", "winmm", "ole32"]

        # osxaudio
        if self.options.get_safe("osxaudio"):
            gst_osxaudio = self.cpp_info.components["gstosxaudio"]
            gst_osxaudio.frameworks = ["CoreAudio", "AudioToolbox"]
            if self.settings.os == "Macos":
                gst_osxaudio.frameworks.extend(["AudioUnit", "CoreServices"])

        # osxvideo
        if self.options.get_safe("osxvideo"):
            gst_osxvideo = self.cpp_info.components["gstosxvideo"]
            gst_osxvideo.frameworks = ["OpenGL", "Cocoa"]

        # qml6
        if self._with_qt:
            qt_major = Version(self.dependencies["qt"].ref.version).major
            qt_plugin = self.cpp_info.components["qml6" if qt_major == 6 else "qmlgl"]
            if self.options.get_safe("with_xorg"):
                qt_plugin.requires.append("gstreamer-gl-x11-1.0")
            if self.options.get_safe("with_wayland"):
                qt_plugin.requires.append("gstreamer-gl-wayland-1.0")
                qt_plugin.requires.append("qt::qtWaylandClient")
            if self.options.get_safe("with_egl"):
                qt_plugin.requires.append("gstreamer-gl-egl-1.0")
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

        # waveform
        if self._is_enabled("waveform"):
            gst_wf = self.cpp_info.components["gstwaveform"]
            gst_wf.system_libs = ["winmm"]

_gstreamer_libs = {
    "base",
    "check",
    "controller",
    "net",
}
_plugins_base_libs = {
    "allocators",
    "app",
    "audio",
    "fft",
    "gl",
    "gl-egl",
    "gl-prototypes",
    "gl-wayland",
    "gl-x11",
    "pbutils",
    "plugins-base",
    "riff",
    "rtp",
    "rtsp",
    "sdp",
    "tag",
    "video",
}

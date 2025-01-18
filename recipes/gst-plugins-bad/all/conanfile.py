import os
import re
import shutil
from pathlib import Path
from functools import lru_cache

import yaml
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run, stdcpp_library, check_min_cppstd
from conan.tools.files import copy, get, rm, rmdir, rename, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, check_min_vs, is_msvc_static_runtime
from conan.tools.scm import Version

# For PkgConfigDeps.set_property()
required_conan_version = ">=2.8"


class GStPluginsBadConan(ConanFile):
    name = "gst-plugins-bad"
    description = ("GStreamer Bad Plug-ins is a set of plug-ins that aren't up to par compared to the rest."
                   "They might be close to being good quality, but they're missing something - be it a good code review, "
                   "some documentation, a set of tests, a real live maintainer, or some actual wide use.")
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    # Most, but not all, plugins are LGPL. For details, see:
    # https://gitlab.freedesktop.org/gstreamer/gstreamer/-/raw/1.24.11/subprojects/gst-plugins-bad/docs/plugins/gst_plugins_cache.json
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_introspection": [True, False],
        "with_libdrm": [True, False],
        "with_libssh2": [True, False],
        "with_libudev": [True, False],
        "with_wayland": [True, False],
        "with_xorg": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_introspection": False,
        "with_libdrm": False,
        "with_libssh2": False,
        "with_libudev": False,
        "with_wayland": False,
        "with_xorg": False,

        # Additionally, all supported plugins can be enabled/disabled using the same option names as in meson_options.txt
    }

    def export(self):
        copy(self, "plugins/*.yml", self.recipe_folder, self.export_folder)

    def init(self):
        options_defaults = {}
        for plugins_yml in Path(self.recipe_folder, "plugins").glob("*.yml"):
            plugins_info = yaml.safe_load(plugins_yml.read_text())
            for plugin, info in plugins_info.items():
                has_ext_deps = any("::" in r for r in info["requires"]) or plugin == "webrtc"
                for opt in info.get("options", [plugin]):
                    options_defaults[opt] = options_defaults.get(opt, True) and not has_ext_deps
        self.options.update(
            {option: [True, False] for option in options_defaults},
            options_defaults
        )

    def export_sources(self):
        export_conandata_patches(self)

    @property
    @lru_cache()
    def _plugins(self):
        version = Version(self.version)
        return yaml.safe_load(Path(self.recipe_folder, "plugins", f"{version.major}.{version.minor}.yml").read_text())

    def _is_enabled(self, plugin):
        required_options = self._plugins[plugin].get("options", [plugin])
        return all(self.options.get_safe(opt, False) for opt in required_options)

    @lru_cache()
    def _plugin_reqs(self, plugin):
        reqs = []
        for req in self._plugins[plugin]["requires"]:
            m = re.fullmatch("gstreamer-(.+)-1.0", req)
            if m and m[1] in _gstreamer_libs:
                reqs.append(f"gstreamer::{m[1]}")
            elif m and m[1] in _plugins_base_libs:
                reqs.append(f"gst-plugins-base::{m[1]}")
            else:
                reqs.append(req)
        return reqs

    @property
    @lru_cache()
    def _all_reqs(self):
        reqs = set()
        for plugin in self._plugins:
            if self._is_enabled(plugin):
                reqs.update(r.split("::")[0] for r in self._plugin_reqs(plugin) if "::" in r)
        return reqs

    @property
    @lru_cache()
    def _all_options(self):
        options = set()
        for plugins_yml in Path(self.recipe_folder, "plugins").glob("*.yml"):
            plugins_info = yaml.safe_load(plugins_yml.read_text())
            for plugin, info in plugins_info.items():
                options.update(info.get("options", [plugin]))
        return options

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shm
            del self.options.unixfd
        else:
            del self.options.amfcodec
            del self.options.d3d11
            del self.options.d3d12
            del self.options.d3dvideosink
            del self.options.directshow
            del self.options.directsound
            del self.options.dwrite
            del self.options.mediafoundation
            del self.options.qt6d3d11
            del self.options.wasapi
            del self.options.wic
            del self.options.win32ipc
            del self.options.winks
            del self.options.winscreencap
        if not is_msvc(self):
            # the required winrt library component only supports MSVC as of v1.24.11
            del self.options.wasapi2
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.dc1394
            del self.options.dvb
            del self.options.fbdev
            del self.options.with_libdrm
            del self.options.with_wayland
            del self.options.with_xorg
            if not is_apple_os(self):
                del self.options.openni2
                del self.options.zbar
                self.options.gtk3 = False
        if not is_apple_os(self):
            del self.options.applemedia
        if self.settings.os not in ["Linux", "Windows"]:
            del self.options.nvcodec
            del self.options.va
        if self.settings.os != "Android":
            del self.options.androidmedia

        # Remove options not used by the current version
        for opt, _ in self.options.items():
            if not opt.startswith("with_") and opt not in ["shared", "fPIC"]:
                if opt not in self._all_options:
                    self.options.rm_safe(opt)

        self.options.onnx = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self._is_enabled("curl"):
            del self.options.with_libssh2
        if not self._is_enabled("vulkan") and not self._is_enabled("rfbsrc"):
            self.options.rm_safe("with_xorg")
        self.options["gstreamer"].shared = self.options.shared
        self.options["gst-plugins-base"].shared = self.options.shared
        self.options["gstreamer"].shared = self.options.with_introspection
        self.options["gst-plugins-base"].shared = self.options.with_introspection
        self.options["gst-plugins-base"].with_gl = "opengl" in self._all_reqs

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        reqs = self._all_reqs
        self.requires(f"gstreamer/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires(f"gst-plugins-base/{self.version}", transitive_headers=True, transitive_libs=True)
        if "gst-orc" in reqs:
            self.requires("gst-orc/0.4.40")
        if self.options.with_introspection:
            self.requires("gobject-introspection/1.78.1")

        if "libaom-av1" in reqs:
            self.requires("libaom-av1/3.8.0")
        if "bzip2" in reqs:
            self.requires("bzip2/1.0.8")
        if "directx-headers" in reqs:
            self.requires("directx-headers/1.614.0")
        if "faac" in reqs:
            self.requires("faac/1.30")
        if "libfdk_aac" in reqs:
            self.requires("libfdk_aac/2.0.3")
        if "google-cloud-cpp" in reqs:
            self.requires("google-cloud-cpp/2.28.0")
        if "gtk" in reqs:
            self.requires("gtk/3.24.43")
        if "json-glib" in reqs:
            self.requires("json-glib/1.10.6")
        if "libcurl" in reqs:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.get_safe("with_libdrm"):
            self.requires("libdrm/2.4.119")
        if "libdc1394" in reqs:
            self.requires("libdc1394/2.2.7")
        if "libqrencode" in reqs:
            self.requires("libqrencode/4.1.1")
        if "libde265" in reqs:
            self.requires("libde265/1.0.15")
        if self._is_enabled("curl") and self.options.with_libssh2:
            self.requires("libssh2/1.11.1", options={"shared": True})
        if "libusb" in reqs:
            self.requires("libusb/1.0.26")
        if "libgudev" in reqs or (self._is_enabled("va") and self.options.get_safe("with_libudev")):
            self.requires("libgudev/238")
        if self._is_enabled("va"):
            self.requires("libva/2.21.0")
        if "libxml2" in reqs:
            self.requires("libxml2/[>=2.12.5 <3]")
        if "lcms" in reqs:
            self.requires("lcms/2.16")
        if "libmodplug" in reqs:
            self.requires("libmodplug/0.8.9.0")
        if self.options.webrtc:
            self.requires("libnice/0.1.21")
        if "onnxruntime" in reqs:
            self.requires("onnxruntime/1.18.1")
        if "openal-soft" in reqs:
            self.requires("openal-soft/1.22.2")
        if "opencv" in reqs:
            # Only < 3.5.0 is supported. 'contrib' is required for opencv_tracking.
            self.requires("opencv/3.4.20", options={"contrib": True})
        if "openexr" in reqs:
            # 3.x is not supported
            self.requires("openexr/2.5.7")
        if "opengl" in reqs:
            self.requires("opengl/system")
        if "openh264" in reqs:
            self.requires("openh264/2.5.0")
        if "openjpeg" in reqs:
            self.requires("openjpeg/2.5.2")
        if "openni2" in reqs:
            self.requires("openni2/2.2.0.33")
        if "opus" in reqs:
            self.requires("opus/1.4")
        if "pango" in reqs:
            self.requires("pango/1.54.0")
        if "qt" in reqs:
            self.requires("qt/[>=6.7 <7]", options={
                "qtdeclarative": True,
                "qtshadertools": True,
                "qttools": can_run(self)
            })
        if "librsvg" in reqs:
            self.requires("librsvg/2.40.21")
        if "usrsctp" in reqs:
            self.requires("usrsctp/0.9.5.0")
        if "libsndfile" in reqs:
            self.requires("libsndfile/1.2.2")
        if "soundtouch" in reqs:
            self.requires("soundtouch/2.3.3")
        if "srt" in reqs:
            self.requires("srt/1.5.3")
        if "libsrtp" in reqs:
            self.requires("libsrtp/2.6.0")
        if "openssl" in reqs:
            self.requires("openssl/[>=1.1 <4]")
        if "libsvtav1" in reqs:
            self.requires("libsvtav1/2.2.1")
        if "tinyalsa" in reqs:
            self.requires("tinyalsa/2.0.0")
        if "vo-amrwbenc" in reqs:
            self.requires("vo-amrwbenc/0.1.3")
        if "libv4l" in reqs:
            self.requires("libv4l/1.28.1")
        if "vulkan-loader" in reqs:
            self.requires("vulkan-loader/1.3.290.0")
            if self.options.get_safe("with_wayland") or self.options.get_safe("with_xorg"):
                self.requires("xkbcommon/1.6.0")
            if is_apple_os(self):
                self.requires("moltenvk/1.2.2")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
        if "libwebp" in reqs:
            self.requires("libwebp/1.3.2")
        if "wildmidi" in reqs:
            self.requires("wildmidi/0.4.5")
        if self.options.get_safe("with_xorg"):
            self.requires("xorg/system")
        if "libx265" in reqs:
            self.requires("libx265/3.4")
        if "zbar" in reqs:
            self.requires("zbar/0.23.92")
        if "zxing-cpp" in reqs:
            self.requires("zxing-cpp/2.2.1")

    def validate(self):
        if (self.options.shared != self.dependencies["gstreamer"].options.shared or
            self.options.shared != self.dependencies["glib"].options.shared or
            self.options.shared != self.dependencies["gst-plugins-base"].options.shared):
                # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
                raise ConanInvalidConfiguration("GLib, GStreamer and GstPlugins must be either all shared, or all static")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} does not support gcc older than 5")
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared build with static runtime is not supported due to the FlsAlloc limit")
        if self.options.curl:
            if is_msvc(self):
                # Requires unistd.h
                raise ConanInvalidConfiguration("-o curl=True is not compatible with MSVC")
            if self.options.with_libssh2 and not self.dependencies["libssh2"].options.shared:
                raise ConanInvalidConfiguration("libssh2 must be built as a shared library")
        if self._is_enabled("directshow") and not is_msvc(self):
            raise ConanInvalidConfiguration("directshow plugin can only be built with MSVC")
        if self._is_enabled("qt6d3d11") or self._is_enabled("zxing"):
            check_min_cppstd(self, 17)
        elif self._is_enabled("nvcodec"):
            check_min_cppstd(self, 14)
        elif self._is_enabled("opencv") or self._is_enabled("applemedia"):
            check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("gettext/0.22.5")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/<host_version>")
        if "gst-orc" in self._all_reqs:
            self.tool_requires("gst-orc/<host_version>")
        if self.options.vulkan:
            self.tool_requires("shaderc/2024.1")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/<host_version>")
            self.tool_requires("wayland-protocols/1.33")
        if self._is_enabled("qt6d3d11") and not can_run(self):
            self.tool_requires("qt/<host_version>", options={
                "qtdeclarative": True,
                "qtshadertools": True,
                "qttools": True
            })

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        # Adjust OpenCV data dir path for Conan
        replace_in_file(self, os.path.join(self.source_folder, "gst-libs", "gst", "opencv", "meson.build"),
                        "'/share/opencv'",
                        "'/res'")

    def generate(self):
        tc = MesonToolchain(self)

        if is_msvc(self) and not check_min_vs(self, 190, raise_invalid=False):
            tc.c_link_args.append("-Dsnprintf=_snprintf")

        if self.settings.get_safe("compiler.runtime"):
            tc.properties["b_vscrt"] = str(self.settings.compiler.runtime).lower()

        def feature(value):
            return "enabled" if value else "disabled"

        opts = self._all_options - {"with_wayland"}
        for opt in opts:
            tc.project_options[opt] = feature(self.options.get_safe(opt))

        # Feature options for plugins that need external deps
        tc.project_options["aja"] = "disabled"  # libajantv2
        tc.project_options["asio"] = "disabled"  # proprietary
        tc.project_options["assrender"] = "disabled"  # libass
        tc.project_options["avtp"] = "disabled"  # avtp
        tc.project_options["bluez"] = "disabled"  # bluez
        tc.project_options["bs2b"] = "disabled"  # libbs2b
        tc.project_options["chromaprint"] = "disabled"  # libchromaprint
        tc.project_options["directfb"] = "disabled"  # directfb
        tc.project_options["dts"] = "disabled"  # libdca (GPL)
        tc.project_options["faad"] = "disabled"  # faad2 (GPL)
        tc.project_options["flite"] = "disabled"  # flite
        tc.project_options["fluidsynth"] = "disabled"  # fluidsynth
        tc.project_options["gme"] = "disabled"  # gme
        tc.project_options["gsm"] = "disabled"  # libgsm1
        tc.project_options["iqa"] = "disabled"  # kornelski/dssim (GPL)
        tc.project_options["isac"] = "disabled"  # webrtc-audio-coding-1
        tc.project_options["ladspa"] = "disabled"  # ladspa-sdk
        tc.project_options["ladspa-rdf"] = "disabled"
        tc.project_options["lc3"] = "disabled"  # lc3
        tc.project_options["ldac"] = "disabled"  # ldacbt
        tc.project_options["lv2"] = "disabled"  # lilv
        tc.project_options["magicleap"] = "disabled"  # proprietary
        tc.project_options["microdns"] = "disabled"  # libmicrodns
        tc.project_options["mpeg2enc"] = "disabled"  # mjpegtools (GPL)
        tc.project_options["mplex"] = "disabled"  # mjpegtools (GPL)
        tc.project_options["msdk"] = "disabled"  # Intel Media SDK or oneVPL SDK
        tc.project_options["musepack"] = "disabled"  # libmpcdec
        tc.project_options["neon"] = "disabled"  # libneon27
        tc.project_options["openaptx"] = "disabled"  # openaptx
        tc.project_options["openmpt"] = "disabled"  # openmpt
        tc.project_options["opensles"] = "disabled"  # opensles
        tc.project_options["resindvd"] = "disabled"  # dvdnav (GPL)
        tc.project_options["rtmp"] = "disabled"  # librtmp
        tc.project_options["sbc"] = "disabled" # libsbc
        tc.project_options["spandsp"] = "disabled"  # spandsp
        tc.project_options["svthevcenc"] = "disabled"  # svt-hevc
        tc.project_options["teletext"] = "disabled"  # zvbi
        tc.project_options["voaacenc"] = "disabled"  # vo-aacenc
        tc.project_options["webrtcdsp"] = "disabled"  # webrtc-audio-processing-1
        tc.project_options["wpe"] = "disabled"  # wpe-webkit

        # D3D11 plugin options
        # option('d3d11-math', type : 'feature', value : 'auto', description : 'Enable DirectX SIMD Math support')
        # option('d3d11-hlsl-precompile', type : 'feature', value : 'auto', description : 'Enable buildtime HLSL compile for d3d11 library/plugin')
        # option('d3d11-wgc', type : 'feature', value : 'auto', description : 'Windows Graphics Capture API support in d3d11 plugin')

        tc.project_options["drm"] = feature(self.options.get_safe("with_libdrm"))
        tc.project_options["udev"] = feature("libgudev" in self._all_reqs or (self._is_enabled("va") and self.options.get_safe("with_libudev")))
        tc.project_options["gl"] = feature("opengl" in self._all_reqs)
        tc.project_options["wayland"] = feature(self.options.get_safe("with_wayland"))
        tc.project_options["x11"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["curl-ssh2"] = feature(self.options.get_safe("with_libssh2"))
        tc.project_options["hls-crypto"] = "openssl"
        tc.project_options["vulkan-video"] = "enabled"
        tc.project_options["sctp-internal-usrsctp"] = "disabled"

        tc.project_options["gpl"] = "enabled"  # only applies to libx265 currently
        tc.project_options["doc"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["nls"] = "enabled"
        tc.project_options["orc"] = feature("gst-orc" in self._all_reqs)
        tc.project_options["introspection"] = "disabled"  # TODO

        if not self.dependencies["gst-orc"].options.shared:
            # The define is not propagated correctly in the Meson build scripts
            tc.extra_defines.append("ORC_STATIC_COMPILATION")

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.set_property("wildmidi", "pkg_config_name", "WildMIDI")
        if self.options.get_safe("with_wayland"):
            deps.build_context_activated.append("wayland-protocols")
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
        pkgconfig_variables = {
            "exec_prefix": "${prefix}",
            "toolsdir": "${exec_prefix}/bin",
            "pluginsdir": "${libdir}/gstreamer-1.0",
            "datarootdir": "${prefix}/res",
            "datadir": "${datarootdir}",
            "girdir": "${datadir}/gir-1.0",
            "typelibdir": "${libdir}/girepository-1.0",
            "libexecdir": "${prefix}/libexec",
            "pluginscannerdir": "${libexecdir}/gstreamer-1.0",
        }
        pkgconfig_custom_content = "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items())

        if self.options.shared:
            self.runenv_info.append_path("GST_PLUGIN_PATH", os.path.join(self.package_folder, "lib", "gstreamer-1.0"))

        if self.options.with_introspection:
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
            self.runenv_info.append_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))

        def _define_library(name, extra_requires, lib=None, interface=False):
            component_name = f"gstreamer-{name}-1.0"
            component = self.cpp_info.components[component_name]
            component.set_property("pkg_config_name", component_name)
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
                "glib::glib-2.0",
                "glib::gobject-2.0",
            ] + extra_requires
            if self.options.with_introspection:
                component.requires.append("gobject-introspection::gobject-introspection")
            component.resdirs = ["res"]
            if not interface:
                component.libs = [lib or f"gst{name.replace('-', '')}-1.0"]
                component.includedirs = [os.path.join("include", "gstreamer-1.0")]
                component.set_property("pkg_config_custom_content", pkgconfig_custom_content)
                if self.settings.os in ["Linux", "FreeBSD"] and not self.options.shared:
                    component.system_libs = ["m", "dl", "rt"]
            return component

        def _define_plugin(name, extra_requires, cpp=False):
            name = f"gst{name}"
            component = self.cpp_info.components[name]
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
                "glib::glib-2.0",
                "glib::gobject-2.0",
            ] + extra_requires
            component.includedirs = []
            component.bindirs = []
            if self.options.shared:
                component.bindirs.append(os.path.join("lib", "gstreamer-1.0"))
            else:
                component.libs = [name]
                component.libdirs = [os.path.join("lib", "gstreamer-1.0")]
                if self.settings.os in ["Linux", "FreeBSD"]:
                    component.system_libs = ["m", "dl"]
                component.defines.append("GST_PLUGINS_BAD_STATIC")
            if cpp and not self.options.shared and stdcpp_library(self):
                component.system_libs.append(stdcpp_library(self))
            return component

        # Libraries

        # adaptivedemux
        _define_library("adaptivedemux", [
            "gstreamer-downloader-1.0",
        ])
        # analytics
        _define_library("analytics", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # bad-audio
        _define_library("bad-audio", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        # bad-base-camerabinsrc
        _define_library("bad-base-camerabinsrc", [
            "gst-plugins-base::gstreamer-app-1.0",
        ], lib="gstbasecamerabinsrc-1.0")
        # codecparsers
        _define_library("codecparsers", [])
        # codecs
        _define_library("codecs", [
            "gstreamer-codecparsers-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        # cuda
        if self.settings.os in ["Linux", "Windows"] and "opengl" in self._all_reqs:
            gst_cuda = _define_library("cuda", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-gl-prototypes-1.0",
                "glib::gmodule-2.0",
                "opengl::opengl",
            ])
            if self.settings.os == "Linux" and self.settings.arch not in ["x86", "x86_64"]:
                gst_cuda.system_libs.append("atomic")
            elif self.settings.os == "Windows":
                gst_cuda.system_libs.append("advapi32")
        # d3d11
        if self._is_enabled("d3d11"):
            gst_d3d11 = _define_library("d3d11", [
                "gst-plugins-base::gstreamer-video-1.0",
            ])
            gst_d3d11.includedirs.append(os.path.join("lib", "gstreamer-1.0", "include"))
            gst_d3d11.system_libs.extend([
                "d3d11", "dxgi", "d3dcompiler", "runtimeobject",
            ])
        # downloader
        _define_library("downloader", [], lib="gsturidownloader-1.0")
        # dxva
        if self.settings.os == "Windows":
            _define_library("dxva", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-codecs-1.0",
            ])
        # insertbin
        _define_library("insertbin", [])
        # isoff
        _define_library("isoff", [])
        # mpegts
        _define_library("mpegts", [])
        # mse
        _define_library("mse", [
            "gst-plugins-base::gstreamer-app-1.0",
        ])
        # opencv
        if self._is_enabled("opencv"):
            _define_library("opencv", [
                "gst-plugins-base::gstreamer-video-1.0",
                "opencv::opencv_core",
            ])
        # photography
        _define_library("photography", [])
        # play
        _define_library("play", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        # player
        _define_library("player", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gstreamer-play-1.0",
        ])
        # sctp
        _define_library("sctp", [])
        # transcoder
        _define_library("transcoder", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        # va
        if self._is_enabled("va"):
            libva = _define_library("va", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "libva::libva_",
            ])
            if self.options.get_safe("with_libdrm"):
                libva.requires.extend([
                    "libva::libva-drm",
                    "libdrm::libdrm_libdrm",
                ])
            if self.settings.os == "Windows":
                libva.requires.append("libva::libva-win32")
                libva.system_libs.append("dxgi")
        # vulkan
        if self.options.get_safe("vulkan"):
            gst_vulkan = _define_library("vulkan", [
                "gst-plugins-base::gstreamer-video-1.0",
                "vulkan-loader::vulkan-loader",
            ])
            if self.options.get_safe("with_wayland"):
                gst_vulkan.requires.append("wayland::wayland-client")
                _define_library("vulkan-wayland", [
                    "gstreamer-vulkan-1.0",
                    "wayland::wayland-client",
                ], interface=True)
            if self.options.get_safe("with_xorg"):
                gst_vulkan.requires.extend([
                    "xorg::xcb",
                    "xkbcommon::libxkbcommon",
                    "xkbcommon::libxkbcommon-x11",
                ])
                _define_library("vulkan-xcb", [
                    "gstreamer-vulkan-1.0",
                    "xorg::xcb",
                ], interface=True)
            if is_apple_os(self):
                gst_vulkan.requires.append("moltenvk::moltenvk")
                gst_vulkan.frameworks.extend([
                    "Foundation", "QuartzCore", "CoreFoundation",
                ])
                if self.settings.os == "Macos":
                    gst_vulkan.frameworks.append("Cocoa")
                else:
                    gst_vulkan.frameworks.append("UIKit")
            elif self.settings.os == "Windows":
                gst_vulkan.system_libs.append("gdi32")
        # wayland
        if self.options.get_safe("with_wayland"):
            gst_wayland = _define_library("wayland", [
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "wayland::wayland-client",
            ])
            if self.options.get_safe("with_libdrm"):
                gst_wayland.requires.append("libdrm::libdrm_libdrm")
        # webrtc
        _define_library("webrtc", [
            "gst-plugins-base::gstreamer-sdp-1.0",
        ])
        # webrtc-nice
        if self._is_enabled("webrtc"):
            _define_library("webrtc-nice", [
                "gst-plugins-base::gstreamer-sdp-1.0",
                "gstreamer-webrtc-1.0",
                "libnice::libnice",
                "glib::gio-2.0",
            ])
        # winrt
        if is_msvc(self):
            gst_winrt = _define_library("winrt", [])
            gst_winrt.system_libs.append("runtimeobject")

        # Plugins

        for plugin, info in self._plugins.items():
            if self._is_enabled(plugin):
                _define_plugin(plugin, self._plugin_reqs(plugin), cpp=info.get("cpp", False))

        # amfcodec
        if self._is_enabled("amfcodec"):
            gst_amfcodec = self.cpp_info.components["gstamfcodec"]
            gst_amfcodec.system_libs.append("winmm")
        # androidmedia
        if self._is_enabled("androidmedia"):
            gst_am = self.cpp_info.components["gstandroidmedia"]
            gst_am.system_libs.extend(["android"])
        # applemedia
        if self._is_enabled("applemedia"):
            gst_applemedia = self.cpp_info.components["gstapplemedia"]
            if self.options.vulkan:
                gst_applemedia.requires.extend([
                    "gstreamer-vulkan-1.0",
                    "moltenvk::moltenvk",
                ])
            gst_applemedia.frameworks.extend([
                "AVFoundation", "AudioToolbox", "CoreFoundation", "CoreMedia",
                "CoreVideo", "IOSurface", "Metal", "VideoToolbox",
            ])
            if self.settings.os == "Macos":
                gst_applemedia.frameworks.extend(["Cocoa", "OpenGL"])
            else:
                gst_applemedia.frameworks.extend(["Foundation", "AssetsLibrary"])
        # curl
        if self._is_enabled("curl") and self.options.with_libssh2:
            gst_curl = self.cpp_info.components["gstcurl"]
            gst_curl.requires.append("libssh2::libssh2")
        # d3d
        if self._is_enabled("d3d") and not self.options.shared:
            gst_d3d = self.cpp_info.components["gstd3d"]
            gst_d3d.system_libs.extend(["d3d9", "gdi32"])
        # d3d11
        if self._is_enabled("d3d11") and not self.options.shared:
            gst_d3d11 = self.cpp_info.components["gstd3d11"]
            gst_d3d11.system_libs.extend([
                "d2d1", "runtimeobject", "winmm", "dwmapi",
            ])
        # d3d12
        if self._is_enabled("d3d12") and not self.options.shared:
            gst_d3d12 = self.cpp_info.components["gstd3d12"]
            gst_d3d12.system_libs.extend(["d3d12", "d3d11", "d2d1", "dxgi"])
        # decklink
        if self._is_enabled("decklink"):
            gst_decklink = self.cpp_info.components["gstdecklink"]
            if self.settings.os == "Windows":
                gst_decklink.system_libs.append("comsuppw")
            elif is_apple_os(self):
                gst_decklink.frameworks.append("CoreFoundation")
            elif self.settings.os in ["Linux", "FreeBSD"]:
                gst_decklink.system_libs.extend(["pthread", "dl"])
        # directshow
        if self._is_enabled("directshow") and not self.options.shared:
            gst_directshow = self.cpp_info.components["gstdirectshow"]
            gst_directshow.system_libs.extend([
                "strmiids", "winmm", "dmoguids", "wmcodecdspuuid", "mfuuid", "rpcrt4",
            ])
        # directsoundsrc
        if self._is_enabled("directsoundsrc") and not self.options.shared:
            gst_directsound = self.cpp_info.components["gstdirectsoundsrc"]
            gst_directsound.system_libs.extend(["dsound", "winmm", "ole32"])
        # dwrite
        if self._is_enabled("dwrite") and self._is_enabled("d3d11") and not self.options.shared:
            gst_dwrite = self.cpp_info.components["gstdwrite"]
            gst_dwrite.system_libs.extend(["d2d1", "dwrite", "windowscodecs"])
        # kms
        if self._is_enabled("kms") and self.options.get_safe("with_libdrm"):
            gst_kms = self.cpp_info.components["gstkms"]
            gst_kms.requires.append("libdrm::libdrm_libdrm")
        # mediafoundation
        if self._is_enabled("mediafoundation"):
            gst_mf = self.cpp_info.components["gstmediafoundation"]
            if self._is_enabled("d3d11"):
                gst_mf.requires.append("gstreamer-d3d11-1.0")
            if not self.options.shared:
                gst_mf.system_libs.extend([
                    "mf", "mfplat", "mfreadwrite", "mfuuid", "strmiids", "ole32", "runtimeobject",
                ])
        # nvcodec
        if self._is_enabled("nvcodec") and self.settings.os == "Windows":
            gst_nvcodec = self.cpp_info.components["gstnvcodec"]
            gst_nvcodec.requires.append("gstreamer-d3d11-1.0")
        # onnx
        if self._is_enabled("onnx") and self.settings.os in ["Linux", "Windows"]:
            gst_onnx = self.cpp_info.components["gstonnx"]
            gst_onnx.requires.append("gstreamer-cuda-1.0")
        if self._is_enabled("rfbsrc") and self.options.get_safe("with_xorg"):
            gst_rfbsrc = self.cpp_info.components["gstrfbsrc"]
            gst_rfbsrc.requires.append("xorg::x11")
        # qsv
        if self._is_enabled("qsv"):
            gst_qsv = self.cpp_info.components["gstqsv"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                gst_qsv.requires.append("gstreamer-va-1.0")
                gst_qsv.system_libs.extend(["pthread", "dl"])
            elif self.settings.os == "Windows":
                gst_qsv.requires.append("gstreamer-d3d11-1.0")
        # va
        if self._is_enabled("va") and self.options.get_safe("with_libudev"):
            gst_va = self.cpp_info.components["gstva"]
            gst_va.requires.append("libgudev::libgudev")
        # wasapi
        if self._is_enabled("wasapi") and not self.options.shared:
            gst_wasapi = self.cpp_info.components["gstwasapi"]
            gst_wasapi.system_libs.extend(["ole32", "ksuser"])
        # wasapi2
        if self._is_enabled("wasapi2") and not self.options.shared:
            gst_wasapi = self.cpp_info.components["gstwasapi2"]
            gst_wasapi.system_libs.extend([
                "ole32", "ksuser", "runtimeobject", "mmdevapi", "mfplat",
            ])
        # wic
        if self._is_enabled("wic") and not self.options.shared:
            gst_wic = self.cpp_info.components["gstwic"]
            gst_wic.system_libs.extend(["windowscodecs"])
        # winks
        if self._is_enabled("winks") and not self.options.shared:
            gst_winks = self.cpp_info.components["gstwinks"]
            gst_winks.system_libs.extend([
                "ksuser", "uuid", "strmiids", "dxguid", "setupapi", "ole32",
            ])
        # winscreencap
        if self._is_enabled("winscreencap") and not self.options.shared:
            gst_winscreencap = self.cpp_info.components["gstwinscreencap"]
            gst_winscreencap.system_libs.extend(["d3d9", "gdi32"])


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

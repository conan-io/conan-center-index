import os
import shutil
from pathlib import Path

from conan import ConanFile
from conan.tools.build import stdcpp_library
from conan.tools.files import copy, get, rm, rmdir, rename, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, check_min_vs

required_conan_version = ">=2.4"


class GStPluginsUglyConan(ConanFile):
    name = "gst-plugins-ugly"
    description = "A set of good-quality plug-ins for GStreamer that might pose distribution problems"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    # Mostly GPL, some LGPL plugins. For details, see:
    # https://gitlab.freedesktop.org/gstreamer/gstreamer/-/raw/1.24.10/subprojects/gst-plugins-ugly/docs/gst_plugins_cache.json
    license = "GPL-2.0-only"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libx264": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libx264": False,
    }
    languages = ["C"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["gstreamer"].shared = self.options.shared
        self.options["gst-plugins-base"].shared = self.options.shared

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"gstreamer/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires(f"gst-plugins-base/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        if self.options.with_libx264:
            self.requires("libx264/cci.20240224")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("gettext/0.22.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # libx264 on CCI uses custom versions, which fail version validation
        replace_in_file(self, os.path.join(self.source_folder, "ext", "x264", "meson.build"),
                        "dependency('x264', version : '>=0.156'",
                        "dependency('x264'")

    def generate(self):
        tc = MesonToolchain(self)

        if is_msvc(self) and not check_min_vs(self, 190, raise_invalid=False):
            tc.c_link_args.append("-Dsnprintf=_snprintf")

        def feature(value):
            return "enabled" if value else "disabled"

        # Feature options for plugins without external deps
        tc.project_options["asfdemux"] = "enabled"
        tc.project_options["dvdlpcmdec"] = "enabled"
        tc.project_options["dvdsub"] = "enabled"
        tc.project_options["realmedia"] = "enabled"

        # Feature options for plugins that need external deps
        tc.project_options["a52dec"] = "disabled"  # liba52
        tc.project_options["cdio"] = "disabled"  # libcdio
        tc.project_options["dvdread"] = "disabled"  # dvdread
        tc.project_options["mpeg2dec"] = "disabled"  # libmpeg2
        tc.project_options["sidplay"] = "disabled"  # sidplay
        tc.project_options["x264"] = feature(self.options.with_libx264)

        # Common options
        tc.project_options["gpl"] = "enabled"
        tc.project_options["doc"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["nls"] = "enabled"
        tc.project_options["orc"] = "disabled"

        tc.generate()

        deps = PkgConfigDeps(self)
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

        def _define_plugin(name, extra_requires, cpp=False):
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
                component.defines.append("GST_PLUGINS_UGLY_STATIC")
            if cpp and not self.options.shared and stdcpp_library(self):
                component.system_libs.append(stdcpp_library(self))
            return component

        _define_plugin("asf", [
            "gst-plugins-base::gstreamer-rtp-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-riff-1.0",
            "gst-plugins-base::gstreamer-rtsp-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-sdp-1.0",
        ])
        _define_plugin("dvdlpcmdec", [
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        _define_plugin("dvdsub", [
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        _define_plugin("realmedia", [
            "gst-plugins-base::gstreamer-rtsp-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-sdp-1.0",
        ])
        if self.options.with_libx264:
            _define_plugin("x264", [
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "libx264::libx264",
            ])

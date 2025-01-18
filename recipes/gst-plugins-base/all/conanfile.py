import os
import re
import shutil
from functools import lru_cache
from pathlib import Path

import yaml
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get, rm, rmdir, rename, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version

required_conan_version = ">=2.4"


class GStPluginsBaseConan(ConanFile):
    name = "gst-plugins-base"
    description = "Base GStreamer plug-ins and helper libraries"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libdrm": [True, False],
        "with_libpng": [True, False],
        "with_libjpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_graphene": [True, False],
        "with_gl": [True, False],
        "with_egl": [True, False],
        "with_wayland": [True, False],
        "with_xorg": [True, False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libdrm": False,
        "with_libpng": False,
        "with_libjpeg": False,
        "with_graphene": False,
        "with_gl": False,
        "with_egl": False,
        "with_wayland": False,
        "with_xorg": False,
        "with_introspection": False,

        # Additionally, all supported plugins can be enabled/disabled using the same option names as in meson_options.txt
    }
    languages = ["C"]

    def export(self):
        copy(self, "plugins/*.yml", self.recipe_folder, self.export_folder)

    def init(self):
        options_defaults = {}
        for plugins_yml in Path(self.recipe_folder, "plugins").glob("*.yml"):
            plugins_info = yaml.safe_load(plugins_yml.read_text())
            for plugin, info in plugins_info.items():
                has_ext_deps = any("::" in r for r in info["requires"] if r != "gst-orc")
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
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.alsa
            del self.options.with_libdrm
            del self.options.with_egl
            del self.options.with_wayland
            del self.options.with_xorg

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_gl:
            self.options.rm_safe("with_egl")
            self.options.rm_safe("with_wayland")
            self.options.rm_safe("with_graphene")
            self.options.rm_safe("with_libpng")
            self.options.rm_safe("with_libjpeg")
        self.options["gstreamer"].shared = self.options.shared
        self.options["gstreamer"].with_introspection = self.options.with_introspection

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        reqs = self._all_reqs
        self.requires(f"gstreamer/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("gst-orc/0.4.40")

        if self.options.with_introspection:
            self.requires("gobject-introspection/1.78.1", libs=False)

        self.requires("zlib/[>=1.2.11 <2]")
        if "libalsa" in reqs:
            self.requires("libalsa/1.2.10")
        if "libdrm" in reqs:
            self.requires("libdrm/2.4.119")
        if "xorg" in reqs or self.options.with_gl and self.options.get_safe("with_xorg"):
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_gl:
            self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
            if self.settings.os == "Windows":
                self.requires("wglext/cci.20200813", transitive_headers=True, transitive_libs=True)
                self.requires("glext/cci.20210420", transitive_headers=True, transitive_libs=True)
                self.requires("khrplatform/cci.20200529", transitive_headers=True, transitive_libs=True)
            if self.options.get_safe("with_egl"):
                self.requires("egl/system", transitive_headers=True, transitive_libs=True)
            if self.options.get_safe("with_wayland"):
                self.requires("wayland/1.22.0", transitive_headers=True, transitive_libs=True)
            if self.options.with_graphene:
                self.requires("graphene/1.10.8")
            if self.options.with_libpng:
                self.requires("libpng/[>=1.6 <2]")
            if self.options.with_libjpeg == "libjpeg":
                self.requires("libjpeg/9e")
            elif self.options.with_libjpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.0.2")
        if "ogg" in reqs:
            self.requires("ogg/1.3.5")
        if "opus" in reqs:
            self.requires("opus/1.4")
        if "theora" in reqs:
            self.requires("theora/1.1.1")
        if "vorbis" in reqs:
            self.requires("vorbis/1.3.7")
        if "pango" in reqs:
            self.requires("pango/1.54.0")

    def validate(self):
        if not self.dependencies["glib"].options.shared and self.options.shared:
            # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
            raise ConanInvalidConfiguration("shared GStreamer cannot link to static GLib")
        if self.options.shared != self.dependencies["gstreamer"].options.shared:
            # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
            raise ConanInvalidConfiguration("GStreamer and GstPlugins must be either all shared, or all static")
        if Version(self.version) >= "1.18.2" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"gst-plugins-base {self.version} does not support gcc older than 5")
        if self.options.with_gl and self.options.get_safe("with_wayland") and not self.options.get_safe("with_egl"):
            raise ConanInvalidConfiguration("OpenGL support with Wayland requires 'with_egl' turned on!")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("gettext/0.22.5")
        self.tool_requires("gst-orc/<host_version>")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/<host_version>")
            self.tool_requires("wayland-protocols/1.36")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def _gl_config(self):
        gl_api = set()
        gl_platform = set()
        gl_winsys = set()  # TODO: winrt, dispamnx, surfaceless, viv-fb, gbm, android
        if self.options.get_safe("with_egl"):
            gl_api.add("opengl")
            gl_platform.add("egl")
            gl_winsys.add("egl")
        if self.options.get_safe("with_xorg"):
            gl_api.add("opengl")
            gl_platform.add("glx")
            gl_winsys.add("x11")
        if self.options.get_safe("with_wayland"):
            gl_api.add("opengl")
            gl_platform.add("egl")
            gl_winsys.add("wayland")
        if self.settings.os == "Macos":
            gl_api.add("opengl")
            gl_platform.add("cgl")
            gl_winsys.add("cocoa")
        elif is_apple_os(self):
            gl_api.add("gles2")
            gl_platform.add("eagl")
            gl_winsys.add("eagl")
        elif self.settings.os == "Windows":
            gl_api.add("opengl")
            gl_platform.add("wgl")
            gl_winsys.add("win32")
        return list(gl_api), list(gl_platform), list(gl_winsys)

    def generate(self):
        tc = MesonToolchain(self)

        if is_msvc(self) and not check_min_vs(self, 190, raise_invalid=False):
            tc.c_link_args.append("-Dsnprintf=_snprintf")

        gl_api, gl_platform, gl_winsys = self._gl_config()

        def feature(value):
            return "enabled" if value else "disabled"

        for opt in self._all_options - {"with_xorg"}:
            tc.project_options[opt] = feature(self.options.get_safe(opt))

        # OpenGL integration library options
        tc.project_options["gl_api"] = gl_api
        tc.project_options["gl_platform"] = gl_platform
        tc.project_options["gl_winsys"] = gl_winsys

        # Feature option for opengl plugin and integration library
        tc.project_options["gl"] = feature(self.options.with_gl)
        tc.project_options["gl-graphene"] = feature(self.options.with_gl and self.options.with_graphene)
        tc.project_options["gl-jpeg"] = feature(self.options.with_gl and self.options.with_libjpeg)
        tc.project_options["gl-png"] = feature(self.options.with_gl and self.options.with_libpng)

        # Feature options
        tc.project_options["cdparanoia"] = "disabled"  # TODO: cdparanoia
        tc.project_options["drm"] = feature(self.options.get_safe("with_libdrm"))
        tc.project_options["libvisual"] = "disabled"  # TODO: libvisual
        tc.project_options["tremor"] = "disabled"  # TODO: tremor - only useful on machines without floating-point support
        tc.project_options["x11"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["xshm"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["xvideo"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["xi"] = feature(self.options.get_safe("with_xorg"))

        # Common feature options
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["tools"] = "disabled"
        tc.project_options["introspection"] = feature(self.options.with_introspection)
        tc.project_options["nls"] = "enabled"
        tc.project_options["orc"] = "enabled"
        tc.project_options["iso-codes"] = "disabled"  # requires iso-codes package

        if not self.dependencies["gst-orc"].options.shared:
            # The define is not propagated correctly in the Meson build scripts
            tc.extra_defines.append("ORC_STATIC_COMPILATION")

        tc.generate()

        deps = PkgConfigDeps(self)
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
        gst_plugins = []

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
            self.runenv_info.define_path("GST_PLUGIN_PATH", os.path.join(self.package_folder, "lib", "gstreamer-1.0"))

        # Libraries
        def _define_library(name, extra_requires, interface=False):
            component_name = f"gstreamer-{name}-1.0"
            component = self.cpp_info.components[component_name]
            component.set_property("pkg_config_name", component_name)
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
                "glib::gobject-2.0",
                "glib::glib-2.0",
            ] + extra_requires
            if self.options.with_introspection:
                component.requires.append("gobject-introspection::gobject-introspection")
            if not interface:
                component.libs = [f"gst{name}-1.0"]
                component.includedirs = [os.path.join("include", "gstreamer-1.0")]
                component.set_property("pkg_config_custom_content", pkgconfig_custom_content)
                if self.settings.os in ["Linux", "FreeBSD"]:
                    component.system_libs = ["m"]
            return component

        gst_plugins_base = _define_library("plugins-base", [])
        gst_plugins_base.libs = []
        if not self.options.shared:
            gst_plugins_base.defines.append("GST_PLUGINS_BASE_STATIC")
            gst_plugins_base.requires.extend(gst_plugins)
        else:
            gst_plugins_base.bindirs.append(os.path.join("lib", "gstreamer-1.0"))

        gst_allocators = _define_library("allocators", [])
        if self.options.get_safe("with_libdrm"):
            gst_allocators.requires.append("libdrm::libdrm")
        _define_library("app", [])
        _define_library("audio", [
            "gstreamer-tag-1.0",
            "gst-orc::gst-orc",
        ])
        _define_library("fft", [])
        _define_library("pbutils", [
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
            "gstreamer-tag-1.0",
        ])
        _define_library("riff", [
            "gstreamer-audio-1.0",
            "gstreamer-tag-1.0",
        ])
        _define_library("rtp", [
            "gstreamer-audio-1.0",
        ])
        gst_rtsp = _define_library("rtsp", [
            "gstreamer-sdp-1.0",
            "glib::gio-2.0",
        ])
        if self.settings.os == "Windows":
            gst_rtsp.system_libs = ["ws2_32"]
        _define_library("sdp", [
            "gstreamer-rtp-1.0",
            "gstreamer-pbutils-1.0",
            "glib::gio-2.0",
        ])
        _define_library("tag", [
            "zlib::zlib",
        ])
        _define_library("video", [
            "gst-orc::gst-orc",
        ])

        if self.options.with_gl:
            gst_gl = _define_library("gl", [
                "gstreamer-allocators-1.0",
                "gstreamer-video-1.0",
                "glib::gmodule-2.0",
                "opengl::opengl",
                # TODO: bcm
            ])
            gst_gl.includedirs.append(os.path.join("lib", "gstreamer-1.0", "include"))
            gl_api, gl_platform, gl_winsys = self._gl_config()
            gl_variables = {
                **pkgconfig_variables,
                "gl_apis": " ".join(gl_api),
                "gl_platforms": " ".join(gl_platform),
                "gl_winsys": " ".join(gl_winsys),
            }
            gl_custom_content = "\n".join(f"{key}={value}" for key, value in gl_variables.items())
            gst_gl.set_property("pkg_config_custom_content", gl_custom_content)

            if self.options.get_safe("with_egl"):
                gst_gl.requires += ["egl::egl"]
            if self.options.get_safe("with_xorg"):
                gst_gl.requires += ["xorg::x11", "xorg::x11-xcb"]
            if self.options.get_safe("with_wayland"):
                gst_gl.requires += [
                    "wayland::wayland-client",
                    "wayland::wayland-cursor",
                    "wayland::wayland-egl",
                ]
            if self.settings.os == "Windows":
                gst_gl.requires += [
                    "glext::glext",
                    "wglext::wglext",
                    "khrplatform::khrplatform",
                ]
                gst_gl.system_libs = ["gdi32"]
            if is_apple_os(self):
                gst_gl.frameworks = [
                    "CoreFoundation",
                    "Foundation",
                    "QuartzCore",
                    "Cocoa",
                ]
            if self.settings.os in ["iOS", "tvOS", "watchOS"]:
                gst_gl.frameworks.extend(["CoreGraphics", "UIkit"])
            gst_gl.includedirs.append("include")
            gst_gl.includedirs.append(os.path.join(os.path.join("lib", "gstreamer-1.0"), "include"))

            _define_library("gl-prototypes", [
                "gstreamer-gl-1.0",
                "opengl::opengl",
            ], interface=True)

            if self.options.get_safe("with_egl"):
                _define_library("gl-egl", [
                    "gstreamer-gl-1.0",
                    "egl::egl",
                ], interface=True)

            if self.options.get_safe("with_wayland"):
                _define_library("gl-wayland", [
                    "gstreamer-gl-1.0",
                    "wayland::wayland-client",
                    "wayland::wayland-egl",
                ], interface=True)

            if self.options.get_safe("with_xorg"):
                _define_library("gl-x11", [
                    "gstreamer-gl-1.0",
                    "xorg::x11-xcb",
                ], interface=True)

        if self.options.with_introspection:
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
            self.runenv_info.append_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))

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
                    component.system_libs = ["m"]
            gst_plugins.append(name)
            return component

        for plugin, info in self._plugins.items():
            if self._is_enabled(plugin):
                _define_plugin(plugin, self._plugin_reqs(plugin))

        if self.options.with_gl:
            gstopengl = _define_plugin("opengl", [
                "gstreamer::gstreamer-controller-1.0",
                "gstreamer-video-1.0",
                "gstreamer-allocators-1.0",
                "opengl::opengl",
                # TODO: bcm
                # TODO: nvbuf_utils
            ])
            if is_apple_os(self):
                gstopengl.frameworks = ["CoreFoundation", "Foundation", "QuartzCore"]
            if self.options.with_graphene:
                gstopengl.requires.append("graphene::graphene-gobject-1.0")
            if self.options.with_libpng:
                gstopengl.requires.append("libpng::libpng")
            if self.options.with_libjpeg == "libjpeg":
                gstopengl.requires.append("libjpeg::libjpeg")
            elif self.options.with_libjpeg == "libjpeg-turbo":
                gstopengl.requires.append("libjpeg-turbo::libjpeg-turbo")
            if self.options.get_safe("with_xorg"):
                gstopengl.requires.append("xorg::x11")

_gstreamer_libs = {
    "base",
    "check",
    "controller",
    "net",
}

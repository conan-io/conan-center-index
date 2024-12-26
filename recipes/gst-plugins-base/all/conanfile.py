import glob
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import chdir, copy, get, rm, rmdir, rename
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, check_min_vs
from conan.tools.scm import Version

required_conan_version = ">=2.4"


class GStPluginsBaseConan(ConanFile):
    name = "gst-plugins-base"
    description = "GStreamer is a development framework for creating applications like media players, video editors, streaming media broadcasters and so on"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libalsa": [True, False],
        "with_libdrm": [True, False],
        "with_libpng": [True, False],
        "with_libjpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_graphene": [True, False],
        "with_pango": [True, False],
        "with_ogg": [True, False],
        "with_opus": [True, False],
        "with_theora": [True, False],
        "with_vorbis": [True, False],
        "with_gl": [True, False],
        "with_egl": [True, False],
        "with_wayland": [True, False],
        "with_xorg": [True, False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libalsa": True,
        "with_libdrm": True,
        "with_libpng": True,
        "with_libjpeg": "libjpeg",
        "with_graphene": True,
        "with_pango": True,
        "with_ogg": True,
        "with_opus": True,
        "with_theora": True,
        "with_vorbis": True,
        "with_gl": True,
        "with_egl": True,
        "with_wayland": True,
        "with_xorg": True,
        "with_introspection": False,
    }
    languages = ["C"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe("with_libalsa")
            self.options.rm_safe("with_libdrm")
            self.options.rm_safe("with_egl")
            self.options.rm_safe("with_wayland")
            self.options.rm_safe("with_xorg")

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
        self.requires(f"gstreamer/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.get_safe("with_libalsa"):
            self.requires("libalsa/1.2.12")
        if self.options.get_safe("with_libdrm"):
            self.requires("libdrm/2.4.119")
        if self.options.get_safe("with_xorg"):
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_gl:
            self.requires("opengl/system")
            if self.settings.os == "Windows":
                self.requires("wglext/cci.20200813", transitive_headers=True, transitive_libs=True)
                self.requires("glext/cci.20210420", transitive_headers=True, transitive_libs=True)
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
        if self.options.with_ogg:
            self.requires("ogg/1.3.5")
        if self.options.with_opus:
            self.requires("opus/1.5.2")
        if self.options.with_theora:
            self.requires("theora/1.1.1")
        if self.options.with_vorbis:
            self.requires("vorbis/1.3.7")
        if self.options.with_pango:
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
        self.tool_requires("glib/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/<host_version>")
            self.tool_requires("wayland-protocols/1.36")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

        if is_msvc(self):
            tc.c_link_args.append("-lws2_32")
            tc.c_args.append(f"-{msvc_runtime_flag(self)}")
            if not check_min_vs(self, 190, raise_invalid=False):
                tc.c_link_args.append("-Dsnprintf=_snprintf")

        gl_api, gl_platform, gl_winsys = self._gl_config()

        def feature(value):
            return "enabled" if value else "disabled"

        # OpenGL integration library options
        tc.project_options["gl_api"] = gl_api
        tc.project_options["gl_platform"] = gl_platform
        tc.project_options["gl_winsys"] = gl_winsys

        # Feature option for opengl plugin and integration library
        tc.project_options["gl"] = feature(self.options.with_gl)
        tc.project_options["gl-graphene"] = feature(self.options.with_gl and self.options.with_graphene)
        tc.project_options["gl-jpeg"] = feature(self.options.with_gl and self.options.with_libjpeg)
        tc.project_options["gl-png"] = feature(self.options.with_gl and self.options.with_libpng)

        # Feature options for plugins with no external deps
        tc.project_options["adder"] = "enabled"
        tc.project_options["app"] = "enabled"
        tc.project_options["audioconvert"] = "enabled"
        tc.project_options["audiomixer"] = "enabled"
        tc.project_options["audiorate"] = "enabled"
        tc.project_options["audioresample"] = "enabled"
        tc.project_options["audiotestsrc"] = "enabled"
        tc.project_options["compositor"] = "enabled"
        tc.project_options["debugutils"] = "enabled"
        tc.project_options["drm"] = feature(self.options.get_safe("with_libdrm"))
        tc.project_options["dsd"] = "enabled"
        tc.project_options["encoding"] = "enabled"
        tc.project_options["gio"] = "enabled"
        tc.project_options["gio-typefinder"] = "enabled"
        tc.project_options["overlaycomposition"] = "enabled"
        tc.project_options["pbtypes"] = "enabled"
        tc.project_options["playback"] = "enabled"
        tc.project_options["rawparse"] = "enabled"
        tc.project_options["subparse"] = "enabled"
        tc.project_options["tcp"] = "enabled"
        tc.project_options["typefind"] = "enabled"
        tc.project_options["videoconvertscale"] = "enabled"
        tc.project_options["videorate"] = "enabled"
        tc.project_options["videotestsrc"] = "enabled"
        tc.project_options["volume"] = "enabled"

        # Feature options for plugins with external deps
        tc.project_options["alsa"] = feature(self.options.get_safe("with_libalsa"))
        tc.project_options["cdparanoia"] = "disabled"  # TODO: cdparanoia
        tc.project_options["libvisual"] = "disabled"  # TODO: libvisual
        tc.project_options["ogg"] = feature(self.options.with_ogg)
        tc.project_options["opus"] = feature(self.options.with_opus)
        tc.project_options["pango"] = feature(self.options.with_pango)
        tc.project_options["theora"] = feature(self.options.with_theora)
        tc.project_options["tremor"] = "disabled"  # TODO: tremor - only useful on machines without floating-point support
        tc.project_options["vorbis"] = feature(self.options.with_vorbis)
        tc.project_options["x11"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["xshm"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["xvideo"] = feature(self.options.get_safe("with_xorg"))
        tc.project_options["xi"] = feature(self.options.get_safe("with_xorg"))

        # Common feature options
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["tools"] = "disabled"
        tc.project_options["introspection"] = feature(self.options.with_introspection)
        tc.project_options["nls"] = "disabled"
        tc.project_options["orc"] = "disabled"  # TODO: orc
        tc.project_options["iso-codes"] = "disabled"  # requires iso-codes package

        tc.generate()

        deps = PkgConfigDeps(self)
        if self.options.get_safe("with_wayland"):
            deps.build_context_activated.append("wayland-protocols")
        if self.options.with_introspection:
            deps.build_context_activated.append("gobject-introspection")
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        if is_msvc(self):
            with chdir(self, path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
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

        def _define_plugin_component(name, extra_requires):
            name = f"gst{name}"
            component = self.cpp_info.components[name]
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
            ] + extra_requires
            if self.options.shared:
                component.bindirs.append(os.path.join("bin", "gstreamer-1.0"))
            else:
                component.libs = [name]
                component.libdirs = [os.path.join("lib", "gstreamer-1.0")]
                if self.settings.os in ["Linux", "FreeBSD"]:
                    component.system_libs = ["m"]
            gst_plugins.append(name)
            return component

        # Plugins ('gst')
        _define_plugin_component("adder", [
            "gstreamer-audio-1.0",
            # TODO: orc
        ])
        _define_plugin_component("app", [
            "gstreamer-app-1.0",
            "gstreamer-tag-1.0",
        ])
        _define_plugin_component("audioconvert", [
            "gstreamer-audio-1.0",
        ])
        _define_plugin_component("audiomixer", [
            "gstreamer-audio-1.0",
            # TODO: orc
        ])
        _define_plugin_component("audiorate", [
            "gstreamer-audio-1.0",
        ])
        _define_plugin_component("audioresample", [
            "gstreamer-audio-1.0",
        ])
        _define_plugin_component("audiotestsrc", [
            "gstreamer-audio-1.0",
        ])
        _define_plugin_component("basedebug", [
            "gstreamer-video-1.0",
        ])
        _define_plugin_component("compositor", [
            "gstreamer-video-1.0",
            # TODO: orc
        ])
        _define_plugin_component("dsd", [
            "gstreamer-audio-1.0",
        ])
        _define_plugin_component("encoding", [
            "gstreamer-video-1.0",
            "gstreamer-pbutils-1.0",
        ])
        _define_plugin_component("gio", [])
        _define_plugin_component("overlaycomposition", [
            "gstreamer-video-1.0",
        ])
        _define_plugin_component("pbtypes", [
            "gstreamer-video-1.0",
        ])
        _define_plugin_component("playback", [
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
            "gstreamer-pbutils-1.0",
            "gstreamer-tag-1.0",
        ])
        _define_plugin_component("rawparse", [
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
        ])
        _define_plugin_component("subparse", [])
        _define_plugin_component("tcp", [
            "gstreamer::gstreamer-net-1.0",
        ])
        _define_plugin_component("typefindfunctions", [
            "gstreamer-pbutils-1.0",
        ])
        _define_plugin_component("videoconvertscale", [
            "gstreamer-video-1.0",
        ])
        _define_plugin_component("videorate", [
            "gstreamer-video-1.0",
        ])
        _define_plugin_component("videotestsrc", [
            "gstreamer-video-1.0",
            # TODO: orc
        ])
        _define_plugin_component("volume", [
            "gstreamer-audio-1.0",
            # TODO: orc
        ])

        # Plugins ('ext')
        if self.options.get_safe("with_libalsa"):
            _define_plugin_component("alsa", [
                "gstreamer-audio-1.0",
                "gstreamer-tag-1.0",
                "libalsa::libalsa",
            ])

        # if self.options.with_cdparanoia:  # TODO: cdparanoia
        #     _define_plugin_component("cdparanoia", [
        #         "gstreamer-audio-1.0",
        #         "cdparanoia::cdparanoia",
        #     ])

        if self.options.with_gl:
            gstopengl = _define_plugin_component("opengl", [
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

        # if self.options.with_libvisual:  # TODO: libvisual
        #     _define_plugin_component("libvisual", [
        #         "gstreamer-audio-1.0",
        #         "gstreamer-video-1.0",
        #         "gstreamer-pbutils-1.0",
        #         "libvisual::libvisual",
        #     ])

        if self.options.with_ogg:
            _define_plugin_component("ogg", [
                "gstreamer-audio-1.0",
                "gstreamer-pbutils-1.0",
                "gstreamer-tag-1.0",
                "gstreamer-riff-1.0",
                "ogg::ogg",
            ])

        if self.options.with_opus:
            _define_plugin_component("opus", [
                "gstreamer-audio-1.0",
                "gstreamer-pbutils-1.0",
                "gstreamer-tag-1.0",
                "opus::opus",
            ])

        if self.options.with_pango:
            _define_plugin_component("pango", [
                "gstreamer-video-1.0",
                "pango::pangocairo",
            ])

        if self.options.with_theora:
            _define_plugin_component("theora", [
                "gstreamer-video-1.0",
                "gstreamer-tag-1.0",
                "theora::theoraenc",
                "theora::theoradec",
            ])

        if self.options.with_vorbis:
            _define_plugin_component("vorbis", [
                "gstreamer-audio-1.0",
                "gstreamer-tag-1.0",
                "vorbis::vorbismain",
                "vorbis::vorbisenc",
            ])

        # if self.options.with_tremor:  # TODO: tremor
        #     _define_plugin_component("ivorbisdec", [
        #         "gstreamer-audio-1.0",
        #         "gstreamer-tag-1.0",
        #         "tremor::tremor",
        #     ])

        # Plugins ('sys')
        if self.options.get_safe("with_xorg"):
            _define_plugin_component("ximagesink", [
                "gstreamer-video-1.0",
                "xorg::x11",
                "xorg::xext",
                "xorg::xi",
            ])
            _define_plugin_component("xvimagesink", [
                "gstreamer-video-1.0",
                "xorg::x11",
                "xorg::xext",
                "xorg::xv",
                "xorg::xi",
            ])

        # Libraries
        def _define_library_component(name, extra_requires, interface=False):
            component_name = f"gstreamer-{name}-1.0"
            component = self.cpp_info.components[component_name]
            component.set_property("pkg_config_name", component_name)
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
            ] + extra_requires
            if not interface:
                component.libs = [f"gst{name}-1.0"]
                component.includedirs = [os.path.join("include", "gstreamer-1.0")]
                component.set_property("pkg_config_custom_content", pkgconfig_custom_content)
                if self.settings.os in ["Linux", "FreeBSD"]:
                    component.system_libs = ["m"]
            return component

        gst_plugins_base = _define_library_component("plugins-base", [])
        gst_plugins_base.libs = []
        if not self.options.shared:
            gst_plugins_base.defines.append("GST_PLUGINS_BASE_STATIC")
            gst_plugins_base.requires.extend(gst_plugins)
        else:
            gst_plugins_base.bindirs.append(os.path.join("lib", "gstreamer-1.0"))

        gst_allocators = _define_library_component("allocators", [])
        if self.options.get_safe("with_libdrm"):
            gst_allocators.requires.append("libdrm::libdrm")
        _define_library_component("app", [])
        _define_library_component("audio", [
            "gstreamer-tag-1.0",
            # TODO: orc
        ])
        _define_library_component("fft", [])
        _define_library_component("pbutils", [
            "gstreamer-audio-1.0",
            "gstreamer-video-1.0",
            "gstreamer-tag-1.0",
        ])
        _define_library_component("riff", [
            "gstreamer-audio-1.0",
            "gstreamer-tag-1.0",
        ])
        _define_library_component("rtp", [
            "gstreamer-audio-1.0",
        ])
        gst_rtsp = _define_library_component("rtsp", [
            "gstreamer-sdp-1.0",
        ])
        if self.settings.os == "Windows":
            gst_rtsp.system_libs = ["ws2_32"]
        _define_library_component("sdp", [
            "gstreamer-rtp-1.0",
        ])
        _define_library_component("tag", [
            "zlib::zlib",
        ])
        _define_library_component("video", [
            # TODO: orc
        ])

        if self.options.with_gl:
            gst_gl = _define_library_component("gl", [
                "gstreamer-allocators-1.0",
                "gstreamer-video-1.0",
                "opengl::opengl",
                # TODO: bcm
            ])
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
                gst_gl.requires.append("wglext::wglext")
                gst_gl.requires.append("glext::glext")
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

            _define_library_component("gl-prototypes", [
                "gstreamer-gl-1.0",
                "opengl::opengl",
            ], interface=True)

            if self.options.get_safe("with_egl"):
                _define_library_component("gl-egl", [
                    "gstreamer-gl-1.0",
                    "egl::egl",
                ], interface=True)

            if self.options.get_safe("with_wayland"):
                _define_library_component("gl-wayland", [
                    "gstreamer-gl-1.0",
                    "wayland::wayland-client",
                    "wayland::wayland-egl",
                ], interface=True)

            if self.options.get_safe("with_xorg"):
                _define_library_component("gl-x11", [
                    "gstreamer-gl-1.0",
                    "xorg::x11-xcb",
                ], interface=True)

        if self.options.with_introspection:
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
            self.buildenv_info.append_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))

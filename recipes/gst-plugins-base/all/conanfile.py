from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, copy, get, rename, rm, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version

import glob
import os

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class GStPluginsBaseConan(ConanFile):
    name = "gst-plugins-base"
    description = "GStreamer is a development framework for creating applications like media players, video editors, " \
                  "streaming media broadcasters and so on"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    license = "GPL-2.0-only"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libalsa": [True, False],
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

    _gl_api = None
    _gl_platform = None
    _gl_winsys = None

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_libalsa
            del self.options.with_wayland
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_egl
            del self.options.with_xorg

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        self.options["gstreamer"].shared = self.options.shared

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("gstreamer/1.29.2", transitive_headers=True, transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.get_safe("with_libalsa"):
            self.requires("libalsa/1.2.13")
        if self.options.get_safe("with_xorg"):
            self.requires("xorg/system")
        if self.options.with_gl:
            self.requires("opengl/system")
            if self.settings.os == "Windows":
                self.requires("wglext/cci.20200813")
                self.requires("glext/cci.20210420")
            if self.options.get_safe("with_egl"):
                self.requires("egl/system")
            if self.options.get_safe("with_wayland"):
                self.requires("wayland/1.24.0")
                self.requires("wayland-protocols/1.45")
            if self.options.with_graphene:
                self.requires("graphene/1.10.8")
            if self.options.with_libpng:
                self.requires("libpng/[>=1.6 <2]")
            if self.options.with_libjpeg == "libjpeg":
                self.requires("libjpeg/9f")
            elif self.options.with_libjpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.1.4.1")
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
        if not self.dependencies.direct_host["glib"].options.shared and self.options.shared:
            # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
            raise ConanInvalidConfiguration("shared GStreamer cannot link to static GLib")
        if self.options.shared != self.dependencies.direct_host["gstreamer"].options.shared:
            # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
            raise ConanInvalidConfiguration("GStreamer and GstPlugins must be either all shared, or all static")
        if Version(self.version) >= "1.18.2" and \
           self.settings.compiler == "gcc" and \
           Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} does not support gcc older than 5")
        if self.options.with_gl and self.options.get_safe("with_wayland") and not self.options.get_safe("with_egl"):
            raise ConanInvalidConfiguration("OpenGL support with Wayland requires 'with_egl' turned on!")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self._is_legacy_one_profile:
            self.tool_requires("glib/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _gl_config(self):
        if not self._gl_api or not self._gl_platform or not self._gl_winsys:
            gl_api = set()
            gl_platform = set()
            gl_winsys = set()  # TODO: winrt, dispamnx, viv-fb, gbm, android
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
            elif self.settings.os in ["iOS", "tvOS", "watchOS"]:
                gl_api.add("gles2")
                gl_platform.add("eagl")
                gl_winsys.add("eagl")
            elif self.settings.os == "Windows":
                gl_api.add("opengl")
                gl_platform.add("wgl")
                gl_winsys.add("win32")
            self._gl_api = list(gl_api)
            self._gl_platform = list(gl_platform)
            self._gl_winsys = list(gl_winsys)
        return self._gl_api, self._gl_platform, self._gl_winsys

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        if self._is_legacy_one_profile:
            VirtualRunEnv(self).generate(scope="build")
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

        gl_api, gl_platform, gl_winsys = self._gl_config()

        tc = MesonToolchain(self)
        if is_msvc(self) and not check_min_vs(self, "190", raise_invalid=False):
            tc.c_args.append("-Dsnprintf=_snprintf")
            tc.project_options["c_std"] = "c99"
        if is_msvc(self):
            tc.c_link_args.append("-lws2_32")
            tc.cpp_link_args.append("-lws2_32")
        tc.project_options["tools"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["doc"] = "disabled"
        tc.project_options["wrap_mode"] = "nofallback"
        tc.project_options["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        tc.project_options["orc"] = "disabled"  # TODO: orc
        tc.project_options["gl"] = "enabled" if self.options.with_gl else "disabled"
        tc.project_options["gl-graphene"] = "enabled" if self.options.with_gl and self.options.with_graphene else "disabled"
        tc.project_options["gl-png"] = "enabled" if self.options.with_gl and self.options.with_libpng else "disabled"
        tc.project_options["gl-jpeg"] = "enabled" if self.options.with_gl and self.options.with_libjpeg else "disabled"
        tc.project_options["gl_api"] = gl_api
        tc.project_options["gl_platform"] = gl_platform
        tc.project_options["gl_winsys"] = gl_winsys
        tc.project_options["alsa"] = "enabled" if self.options.get_safe("with_libalsa") else "disabled"
        tc.project_options["cdparanoia"] = "disabled"  # TODO: cdparanoia
        tc.project_options["libvisual"] = "disabled"  # TODO: libvisual
        tc.project_options["ogg"] = "enabled" if self.options.with_ogg else "disabled"
        tc.project_options["opus"] = "enabled" if self.options.with_opus else "disabled"
        tc.project_options["pango"] = "enabled" if self.options.with_pango else "disabled"
        tc.project_options["theora"] = "enabled" if self.options.with_theora else "disabled"
        tc.project_options["tremor"] = "disabled"  # TODO: tremor
        tc.project_options["vorbis"] = "enabled" if self.options.with_vorbis else "disabled"
        tc.project_options["x11"] = "enabled" if self.options.get_safe("with_xorg") else "disabled"
        tc.project_options["xshm"] = "enabled" if self.options.get_safe("with_xorg") else "disabled"
        tc.project_options["xvideo"] = "enabled" if self.options.get_safe("with_xorg") else "disabled"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        # regression in 1.16
        if is_msvc(self):
            with chdir(self, path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "gstreamer-1.0", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        gst_plugins = []
        gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        gst_include_path = os.path.join(self.package_folder, "include", "gstreamer-1.0")

        pkgconfig_variables = {
            "exec_prefix": "${prefix}",
            "toolsdir": "${exec_prefix}/bin",
            "pluginsdir": "${libdir}/gstreamer-1.0",
            "datarootdir": "${prefix}/share",
            "datadir": "${datarootdir}",
            "girdir": "${datadir}/gir-1.0",
            "typelibdir": "${libdir}/girepository-1.0",
            "libexecdir": "${prefix}/libexec",
        }
        pkgconfig_custom_content = "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items())

        if self.options.shared:
            self.runenv_info.append_path("GST_PLUGIN_PATH", gst_plugin_path)
            # TODO: remove the following when only Conan 2.0 is supported
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)

        # Plugins are only linkable in static builds; in shared builds they are
        # loaded dynamically at runtime via GST_PLUGIN_PATH.
        def _define_plugin(name, requires, system_libs=None, frameworks=None):
            # Only register the plugin if its library was actually built and installed,
            # since the available plugin set varies across gstreamer versions.
            lib_candidates = [f"lib{name}.a", f"{name}.lib", f"lib{name}.so", f"lib{name}.dylib", f"{name}.dll"]
            if not any(os.path.exists(os.path.join(gst_plugin_path, candidate)) for candidate in lib_candidates):
                return
            component = self.cpp_info.components[name]
            component.libs = [name]
            component.libdirs.append(gst_plugin_path)
            component.requires = requires
            if system_libs:
                component.system_libs = system_libs
            if frameworks:
                component.frameworks = frameworks
            gst_plugins.append(name)

        if not self.options.shared:
            _m = ["m"] if self.settings.os == "Linux" else None

            # Plugins ('gst')
            _define_plugin("gstadder", ["gstreamer-audio-1.0"])  # TODO: orc
            _define_plugin("gstapp", ["gstreamer::gstreamer-base-1.0", "gstreamer-app-1.0", "gstreamer-tag-1.0"])
            _define_plugin("gstaudioconvert", ["gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0"])
            _define_plugin("gstaudiomixer", ["gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0"])  # TODO: orc
            _define_plugin("gstaudiorate", ["gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0"])
            _define_plugin("gstaudioresample", ["gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0"], system_libs=_m)
            _define_plugin("gstaudiotestsrc", ["gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0"], system_libs=_m)
            _define_plugin("gstcompositor", ["gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0"], system_libs=_m)  # TODO: orc
            _define_plugin("gstencoding", ["gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0", "gstreamer-pbutils-1.0"])
            _define_plugin("gstgio", ["gstreamer::gstreamer-base-1.0", "glib::gio-2.0"])
            _define_plugin("gstoverlaycomposition", ["gstreamer-video-1.0"])
            _define_plugin("gstpbtypes", ["gstreamer-video-1.0"])
            _define_plugin("gstplayback", ["gstreamer-audio-1.0", "gstreamer-video-1.0", "gstreamer-pbutils-1.0", "gstreamer-tag-1.0"])
            _define_plugin("gstrawparse", ["gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0", "gstreamer-video-1.0"])
            _define_plugin("gstsubparse", ["gstreamer::gstreamer-base-1.0"])
            _define_plugin("gsttcp", ["gstreamer::gstreamer-base-1.0", "gstreamer::gstreamer-net-1.0", "glib::gio-2.0"])
            _define_plugin("gsttypefindfunctions", ["gstreamer::gstreamer-base-1.0", "gstreamer-pbutils-1.0", "glib::gio-2.0"])
            _define_plugin("gstvideoconvert", ["gstreamer-video-1.0"])
            _define_plugin("gstvideorate", ["gstreamer-video-1.0"])
            _define_plugin("gstvideoscale", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0", "glib::glib-2.0", "glib::gobject-2.0"])
            _define_plugin("gstvideotestsrc", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0", "glib::glib-2.0", "glib::gobject-2.0"], system_libs=_m)  # TODO: orc
            _define_plugin("gstvolume", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0", "glib::glib-2.0", "glib::gobject-2.0"])  # TODO: orc

            # Plugins ('ext')
            if self.options.get_safe("with_libalsa"):
                _define_plugin("gstalsa", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0", "gstreamer-tag-1.0", "libalsa::libalsa", "glib::glib-2.0", "glib::gobject-2.0"])

            if self.options.with_gl:
                gstopengl_requires = ["gstreamer::gstreamer-base-1.0", "gstreamer::gstreamer-controller-1.0", "gstreamer-video-1.0", "gstreamer-allocators-1.0", "opengl::opengl"]  # TODO: bcm, nvbuf_utils
                if self.options.with_graphene:
                    gstopengl_requires.append("graphene::graphene-gobject-1.0")
                if self.options.with_libpng:
                    gstopengl_requires.append("libpng::libpng")
                if self.options.with_libjpeg == "libjpeg":
                    gstopengl_requires.append("libjpeg::libjpeg")
                elif self.options.with_libjpeg == "libjpeg-turbo":
                    gstopengl_requires.append("libjpeg-turbo::libjpeg-turbo")
                if self.options.get_safe("with_xorg"):
                    gstopengl_requires.append("xorg::x11")
                _define_plugin("gstopengl", gstopengl_requires, system_libs=_m,
                               frameworks=["CoreFoundation", "Foundation", "QuartzCore"] if self.settings.os == "Macos" else None)

            if self.options.with_ogg:
                _define_plugin("gstogg", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0", "gstreamer-pbutils-1.0", "gstreamer-tag-1.0", "gstreamer-riff-1.0", "ogg::ogglib", "glib::glib-2.0", "glib::gobject-2.0"])

            if self.options.with_opus:
                _define_plugin("gstopus", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0", "gstreamer-pbutils-1.0", "gstreamer-tag-1.0", "opus::libopus", "glib::glib-2.0", "glib::gobject-2.0"], system_libs=_m)

            if self.options.with_pango:
                _define_plugin("gstpango", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0", "pango::pangocairo", "glib::glib-2.0", "glib::gobject-2.0"], system_libs=_m)

            if self.options.with_theora:
                _define_plugin("gsttheora", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0", "gstreamer-tag-1.0", "theora::theoraenc", "theora::theoradec", "glib::glib-2.0", "glib::gobject-2.0"])

            if self.options.with_vorbis:
                _define_plugin("gstvorbis", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0", "gstreamer-tag-1.0", "vorbis::vorbismain", "vorbis::vorbisenc", "glib::glib-2.0", "glib::gobject-2.0"])

            # Plugins ('sys')
            if self.options.get_safe("with_xorg"):
                _define_plugin("gstximagesink", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0", "xorg::x11", "xorg::xext", "glib::glib-2.0", "glib::gobject-2.0"])
                _define_plugin("gstxvimagesink", ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-video-1.0", "xorg::x11", "xorg::xext", "xorg::xv", "glib::glib-2.0", "glib::gobject-2.0"], system_libs=_m)


        # Libraries
        self.cpp_info.components["gstreamer-plugins-base-1.0"].set_property("pkg_config_name", "gstreamer-plugins-base-1.0")
        self.cpp_info.components["gstreamer-plugins-base-1.0"].requires = ["gstreamer::gstreamer-1.0"]
        self.cpp_info.components["gstreamer-plugins-base-1.0"].includedirs = [gst_include_path]
        if not self.options.shared:
            self.cpp_info.components["gstreamer-plugins-base-1.0"].defines.append("GST_PLUGINS_BASE_STATIC")
            self.cpp_info.components["gstreamer-plugins-base-1.0"].requires.extend(gst_plugins)
        else:
            self.cpp_info.components["gstreamer-plugins-base-1.0"].bindirs.append(gst_plugin_path)
        self.cpp_info.components["gstreamer-plugins-base-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-allocators-1.0"].set_property("pkg_config_name", "gstreamer-allocators-1.0")
        self.cpp_info.components["gstreamer-allocators-1.0"].libs = ["gstallocators-1.0"]
        self.cpp_info.components["gstreamer-allocators-1.0"].requires = ["gstreamer::gstreamer-1.0"]
        self.cpp_info.components["gstreamer-allocators-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-allocators-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-app-1.0"].set_property("pkg_config_name", "gstreamer-app-1.0")
        self.cpp_info.components["gstreamer-app-1.0"].libs = ["gstapp-1.0"]
        self.cpp_info.components["gstreamer-app-1.0"].requires = ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0"]
        self.cpp_info.components["gstreamer-app-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-app-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-audio-1.0"].set_property("pkg_config_name", "gstreamer-audio-1.0")
        self.cpp_info.components["gstreamer-audio-1.0"].libs = ["gstaudio-1.0"]
        self.cpp_info.components["gstreamer-audio-1.0"].requires = ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-tag-1.0"]  # TODO: orc
        self.cpp_info.components["gstreamer-audio-1.0"].includedirs = [gst_include_path]
        if self.settings.os == "Linux":
            self.cpp_info.components["gstreamer-audio-1.0"].system_libs = ["m"]
        self.cpp_info.components["gstreamer-audio-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-fft-1.0"].set_property("pkg_config_name", "gstreamer-fft-1.0")
        self.cpp_info.components["gstreamer-fft-1.0"].libs = ["gstfft-1.0"]
        self.cpp_info.components["gstreamer-fft-1.0"].requires = ["gstreamer::gstreamer-1.0"]
        self.cpp_info.components["gstreamer-fft-1.0"].includedirs = [gst_include_path]
        if self.settings.os == "Linux":
            self.cpp_info.components["gstreamer-fft-1.0"].system_libs = ["m"]
        self.cpp_info.components["gstreamer-fft-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        if self.options.with_gl:
            gl_api, gl_platform, gl_winsys = self._gl_config()
            gl_variables = {
                **pkgconfig_variables,
                "gl_apis": " ".join(gl_api),
                "gl_platforms": " ".join(gl_platform),
                "gl_winsys": " ".join(gl_winsys),
            }
            gl_custom_content = "\n".join(f"{key}={value}" for key, value in gl_variables.items())

            self.cpp_info.components["gstreamer-gl-1.0"].set_property("pkg_config_name", "gstreamer-gl-1.0")
            self.cpp_info.components["gstreamer-gl-1.0"].libs = ["gstgl-1.0"]
            self.cpp_info.components["gstreamer-gl-1.0"].requires = [
                "gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0",
                "gstreamer-allocators-1.0", "gstreamer-video-1.0",
                "glib::gmodule-no-export-2.0", "opengl::opengl"]  # TODO: bcm
            if self.options.get_safe("with_egl"):
                self.cpp_info.components["gstreamer-gl-1.0"].requires.extend(["egl::egl"])
            if self.options.get_safe("with_xorg"):
                self.cpp_info.components["gstreamer-gl-1.0"].requires.extend(["xorg::x11", "xorg::x11-xcb"])
            if self.options.get_safe("with_wayland"):
                self.cpp_info.components["gstreamer-gl-1.0"].requires.extend([
                    "wayland::wayland-client", "wayland::wayland-cursor", "wayland::wayland-egl",
                    "wayland-protocols::wayland-protocols"])
            if self.settings.os == "Windows":
                self.cpp_info.components["gstreamer-gl-1.0"].requires.append("wglext::wglext")
                self.cpp_info.components["gstreamer-gl-1.0"].requires.extend(["glext::glext"])
                self.cpp_info.components["gstreamer-gl-1.0"].system_libs = ["gdi32"]
            if self.settings.os in ["Macos", "iOS", "tvOS", "watchOS"]:
                self.cpp_info.components["gstreamer-gl-1.0"].frameworks = ["CoreFoundation", "Foundation", "QuartzCore", "Cocoa"]
            if self.settings.os in ["iOS", "tvOS", "watchOS"]:
                self.cpp_info.components["gstreamer-gl-1.0"].frameworks.extend(["CoreGraphics", "UIkit"])
            self.cpp_info.components["gstreamer-gl-1.0"].includedirs = [os.path.join(self.package_folder, "include"), gst_include_path]
            self.cpp_info.components["gstreamer-gl-1.0"].includedirs.append(os.path.join(gst_plugin_path, "include"))
            self.cpp_info.components["gstreamer-gl-1.0"].set_property("pkg_config_custom_content", gl_custom_content)

            self.cpp_info.components["gstreamer-gl-prototypes-1.0"].set_property("pkg_config_name", "gstreamer-gl-prototypes-1.0")
            self.cpp_info.components["gstreamer-gl-prototypes-1.0"].requires = ["gstreamer-gl-1.0", "opengl::opengl"]

            if self.options.get_safe("with_egl"):
                self.cpp_info.components["gstreamer-gl-egl-1.0"].set_property("pkg_config_name", "gstreamer-gl-egl-1.0")
                self.cpp_info.components["gstreamer-gl-egl-1.0"].requires = ["gstreamer-gl-1.0", "egl::egl"]

            if self.options.get_safe("with_wayland"):
                self.cpp_info.components["gstreamer-gl-wayland-1.0"].set_property("pkg_config_name", "gstreamer-gl-wayland-1.0")
                self.cpp_info.components["gstreamer-gl-wayland-1.0"].requires = [
                    "gstreamer-gl-1.0", "wayland::wayland-client", "wayland::wayland-egl",
                    "wayland-protocols::wayland-protocols"]

            if self.options.get_safe("with_xorg"):
                self.cpp_info.components["gstreamer-gl-x11-1.0"].set_property("pkg_config_name", "gstreamer-gl-x11-1.0")
                self.cpp_info.components["gstreamer-gl-x11-1.0"].requires = ["gstreamer-gl-1.0", "xorg::x11-xcb"]

        self.cpp_info.components["gstreamer-pbutils-1.0"].set_property("pkg_config_name", "gstreamer-pbutils-1.0")
        self.cpp_info.components["gstreamer-pbutils-1.0"].libs = ["gstpbutils-1.0"]
        self.cpp_info.components["gstreamer-pbutils-1.0"].requires = [
            "gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0",
            "gstreamer-audio-1.0", "gstreamer-video-1.0", "gstreamer-tag-1.0"]
        self.cpp_info.components["gstreamer-pbutils-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-pbutils-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-riff-1.0"].set_property("pkg_config_name", "gstreamer-riff-1.0")
        self.cpp_info.components["gstreamer-riff-1.0"].libs = ["gstriff-1.0"]
        self.cpp_info.components["gstreamer-riff-1.0"].requires = ["gstreamer::gstreamer-1.0", "gstreamer-audio-1.0", "gstreamer-tag-1.0"]
        self.cpp_info.components["gstreamer-riff-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-riff-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-rtp-1.0"].set_property("pkg_config_name", "gstreamer-rtp-1.0")
        self.cpp_info.components["gstreamer-rtp-1.0"].libs = ["gstrtp-1.0"]
        self.cpp_info.components["gstreamer-rtp-1.0"].requires = ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "gstreamer-audio-1.0"]
        self.cpp_info.components["gstreamer-rtp-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-rtp-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-rtsp-1.0"].set_property("pkg_config_name", "gstreamer-rtsp-1.0")
        self.cpp_info.components["gstreamer-rtsp-1.0"].libs = ["gstrtsp-1.0"]
        self.cpp_info.components["gstreamer-rtsp-1.0"].requires = [
            "gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0",
            "gstreamer-sdp-1.0", "glib::gio-2.0"]
        if self.settings.os == "Linux":
            self.cpp_info.components["gstreamer-rtsp-1.0"].system_libs = ["m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["gstreamer-rtsp-1.0"].system_libs = ["ws2_32"]
        self.cpp_info.components["gstreamer-rtsp-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-rtsp-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-sdp-1.0"].set_property("pkg_config_name", "gstreamer-sdp-1.0")
        self.cpp_info.components["gstreamer-sdp-1.0"].libs = ["gstsdp-1.0"]
        self.cpp_info.components["gstreamer-sdp-1.0"].requires = ["gstreamer::gstreamer-1.0", "gstreamer-rtp-1.0", "glib::glib-2.0", "glib::gio-2.0"]
        self.cpp_info.components["gstreamer-sdp-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-sdp-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-tag-1.0"].set_property("pkg_config_name", "gstreamer-tag-1.0")
        self.cpp_info.components["gstreamer-tag-1.0"].libs = ["gsttag-1.0"]
        self.cpp_info.components["gstreamer-tag-1.0"].requires = ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0", "zlib::zlib"]
        if self.settings.os == "Linux":
            self.cpp_info.components["gstreamer-tag-1.0"].system_libs = ["m"]
        self.cpp_info.components["gstreamer-tag-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-tag-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

        self.cpp_info.components["gstreamer-video-1.0"].set_property("pkg_config_name", "gstreamer-video-1.0")
        self.cpp_info.components["gstreamer-video-1.0"].libs = ["gstvideo-1.0"]
        self.cpp_info.components["gstreamer-video-1.0"].requires = ["gstreamer::gstreamer-1.0", "gstreamer::gstreamer-base-1.0"]  # TODO: orc
        if self.settings.os == "Linux":
            self.cpp_info.components["gstreamer-video-1.0"].system_libs = ["m"]
        self.cpp_info.components["gstreamer-video-1.0"].includedirs = [gst_include_path]
        self.cpp_info.components["gstreamer-video-1.0"].set_property("pkg_config_custom_content", pkgconfig_custom_content)

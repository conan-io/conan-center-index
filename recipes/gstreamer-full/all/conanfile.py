from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=2.3.0"

# From subprojects/gst-plugins-base/meson_options.txt
GST_BASE_MESON_OPTIONS = {
    'adder',
    'app',
    'audioconvert',
    'audiomixer',
    'audiorate',
    'audioresample',
    'audiotestsrc',
    'compositor',
    'debugutils',
    'drm',
    'dsd',
    'encoding',
    'gio',
    'gio-typefinder',
    'overlaycomposition',
    'pbtypes',
    'playback',
    'rawparse',
    'subparse',
    'tcp',
    'typefind',
    'videoconvertscale',
    'videorate',
    'videotestsrc',
    'volume',
}

GST_BASE_MESON_OPTIONS_WITH_EXT_DEPS = {
    'alsa',
#    'cdparanoia', # cdparanoia is not available in conan-center
#    'libvisual', # libvisual is not available in conan-center
    'ogg',
    'opus',
    'pango',
    'theora',
#    #'tremor', # tremor is not available in conan-center
    'vorbis',
    'x11',
    'xshm',
    'xvideo',
    'xi',
}

GST_BASE_MESON_OPTIONS_GL = {
    'gl',
    'gl_graphene',
    'gl_png',
}

GST_GOOD_MESON_OPTIONS = {
    'alpha',
    'apetag',
    'audiofx',
    'audioparsers',
    'auparse',
    'autodetect',
    'avi',
    'cutter',
    'debugutils',
    'deinterlace',
    'dtmf',
    'effectv',
    'equalizer',
    'flv',
    'flx',
    'goom',
    'goom2k1',
    'icydemux',
    'id3demux',
    'imagefreeze',
    'interleave',
    'isomp4',
    'law',
    'level',
    'matroska',
    'monoscope',
    'multifile',
    'multipart',
    'replaygain',
    'rtp',
    'rtpmanager',
    'rtsp',
    'shapewipe',
    'smpte',
    'spectrum',
    'udp',
    'videobox',
    'videocrop',
    'videofilter',
    'videomixer',
    'wavenc',
    'wavparse',
    'xingmux',
    'y4m',
}

GST_BAD_MESON_OPTIONS = {
    'accurip',
    'adpcmdec',
    'adpcmenc',
    'aiff',
    #'analyticsoverlay', # require pangocairo
    'asfmux',
    'audiobuffersplit',
    'audiofxbad',
    'audiolatency',
    'audiomixmatrix',
    'audiovisualizers',
    'autoconvert',
    'bayer',
    'camerabin2',
    #'codec2json',
    'codecalpha',
    'codectimestamper',
    'coloreffects',
    'debugutils',
    'dvbsubenc',
    'dvbsuboverlay',
    'dvdspu',
    'faceoverlay',
    'festival',
    'fieldanalysis',
    'freeverb',
    'frei0r',
    'gaudieffects',
    'gdp',
    'geometrictransform',
    'id3tag',
    'insertbin',
    'inter',
    'interlace',
    'ivfparse',
    'ivtc',
    'jp2kdecimator',
    'jpegformat',
    'librfb',
    'midi',
    'mpegdemux',
    'mpegpsmux',
    'mpegtsdemux',
    'mpegtsmux',
    'mse',
    'mxf',
    'netsim',
    'onvif',
    'pcapparse',
    'pnm',
    'proxy',
    'rawparse',
    'removesilence',
    'rist',
    'rtmp2',
    'rtp',
    'sdp',
    'segmentclip',
    'siren',
    'smooth',
    'speed',
    'subenc',
    'switchbin',
    'timecode',
    'unixfd',
    'videofilters',
    'videoframe_audiolevel',
    'videoparsers',
    'videosignal',
    'vmnc',
    'y4m',
}

GST_UGLY_MESON_OPTIONS = {
    'asfdemux',
    'dvdlpcmdec',
    'dvdsub',
    'realmedia',
}

GST_RTSP_SERVER_MESON_OPTIONS = {
    'rtspclientsink',
}

class PackageConan(ConanFile):
    name = "gstreamer-full"
    description = "GStreamer multimedia framework: full set of plugins and libraries"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/gstreamer/gstreamer"
    topics = ("audio", "multimedia", "streaming", "video")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_base": [True, False],
        "with_good": [True, False],
        "with_ugly": [True, False],
        "with_bad": [True, False],
        "with_libav": [True, False],
        "with_rtsp_server": [True, False],

        "with_orc": [True, False],
        "with_introspection": [True, False],
        "with_coretracers": [True, False],

        "with_tools": [True, False],

        "gst_base_audioresample_format": ["auto", "int", "float"],
        "gst_base_gl_jpeg": ["disabled", "libjpeg", "libjpeg-turbo"],

        # conan center packages / system
        "with_egl": [True, False],
        "with_wayland": [True, False],
        "with_xorg": [True, False],
    }
    options.update({f'gst_base_{_name}': [True, False] for _name in GST_BASE_MESON_OPTIONS})
    options.update({f'gst_base_{_name}': [True, False] for _name in GST_BASE_MESON_OPTIONS_WITH_EXT_DEPS})
    options.update({f'gst_base_{_name}': [True, False] for _name in GST_BASE_MESON_OPTIONS_GL})
    options.update({f'gst_good_{_name}': [True, False] for _name in GST_GOOD_MESON_OPTIONS})
    options.update({f'gst_bad_{_name}': [True, False] for _name in GST_BAD_MESON_OPTIONS})
    options.update({f'gst_ugly_{_name}': [True, False] for _name in GST_UGLY_MESON_OPTIONS})
    options.update({f'gst_rtsp_server_{_name}': [True, False] for _name in GST_RTSP_SERVER_MESON_OPTIONS})

    default_options = {
        "with_base": True,
        "with_good": True,
        "with_ugly": True,
        "with_bad": True,
        "with_libav": True,
        "with_rtsp_server": True,

        "with_orc": True,
        "with_introspection": False, # 1.72 is not yet compatible with conan 2.0
        "with_coretracers": False,

        "with_tools": False,

        "gst_base_audioresample_format": "auto",
        "gst_base_gl_jpeg": "libjpeg",

        "with_egl": True,
        "with_wayland": True,
        "with_xorg": True,
    }
    default_options.update({f'gst_base_{_name}': True for _name in GST_BASE_MESON_OPTIONS})
    default_options.update({f'gst_base_{_name}': True for _name in GST_BASE_MESON_OPTIONS_WITH_EXT_DEPS})
    default_options.update({f'gst_base_{_name}': True for _name in GST_BASE_MESON_OPTIONS_GL})
    default_options.update({f'gst_good_{_name}': True for _name in GST_GOOD_MESON_OPTIONS})
    default_options.update({f'gst_bad_{_name}': False for _name in GST_BAD_MESON_OPTIONS})
    default_options.update({f'gst_ugly_{_name}': False for _name in GST_UGLY_MESON_OPTIONS})
    default_options.update({f'gst_rtsp_server_{_name}': False for _name in GST_RTSP_SERVER_MESON_OPTIONS})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os != "Linux":
            self.options.rm_safe('with_wayland')
            self.options.rm_safe('with_alsa')
            self.options.rm_safe('gst_base_x11')
            self.options.rm_safe('gst_base_xvideo')
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe('with_egl')
            self.options.rm_safe('with_xorg')

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)

        if self.options.with_base:
            self.requires("zlib/1.3.1", transitive_headers=True, transitive_libs=True)
            self.requires("libdrm/2.4.120", transitive_headers=True, transitive_libs=True)

        if self.options.with_libav:
            self.requires("ffmpeg/6.1", transitive_headers=True, transitive_libs=True)

        if self.options.get_safe("gst_base_alsa"):
            self.requires("libalsa/1.2.10")
        if self.options.get_safe("gst_base_ogg"):
            self.requires("ogg/1.3.5")
        if self.options.get_safe("gst_base_opus"):
            self.requires("opus/1.4")
        if self.options.get_safe("gst_base_pango"):
            self.requires("pango/1.51.0")
        if self.options.get_safe("gst_base_theora"):
            self.requires("theora/1.1.1")
        if self.options.get_safe("gst_base_vorbis"):
            self.requires("vorbis/1.3.7")
        if self.options.get_safe("with_xorg"):
            self.requires("xorg/system")

        if self.options.get_safe("gst_base_gl"):
            self.requires("opengl/system")
            if self.settings.os == "Windows":
                self.requires("wglext/cci.20200813")
                self.requires('glext/cci.20210420')
            if self.options.get_safe("with_egl"):
                self.requires("egl/system")
            if self.options.get_safe("with_wayland"):
                self.requires("wayland/1.20.0")
                self.requires("wayland-protocols/1.33")
            if self.options.get_safe("gst_base_gl_graphene"):
                self.requires("graphene/1.10.8")
            if self.options.get_safe("gst_base_gl_png"):
                self.requires("libpng/1.6.43")
            if self.options.get_safe("gst_base_gl_jpeg") == "libjpeg":
                self.requires("libjpeg/9e")
            elif self.options.get_safe("gst_base_gl_jpeg") == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.0.2")

    def validate(self):
        # TODO validate if still the case
        if self.dependencies.direct_host["glib"].options.shared:
            raise ConanInvalidConfiguration("GLib must be built as a static library")

        # Need rework, do we even need this???
        #if not self.options.get_safe("gst_base_gl") and (self.options.get_safe("gst_base_gl_graphene") or self.options.get_safe("gst_base_gl_jpeg") != "disabled" or self.options.get_safe("gst_base_gl_png")):
        #    raise ConanInvalidConfiguration("gst_base_gl_graphene, gst_base_gl_jpeg and gst_base_gl_png require gst_base_gl")

        if not self.options.with_base and self.options.with_libav:
            raise ConanInvalidConfiguration("libav is only available with base")

        self._validate_gl_config()

    def build_requirements(self):
        self.tool_requires("meson/1.3.1")

        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")

        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def _get_gl_api(self):
        gl_api = set()
        if self.options.get_safe("with_egl") or \
           self.options.get_safe("with_xorg") or \
           self.options.get_safe("with_wayland") or \
           self.settings.os == "Macos" or \
           self.settings.os == "Windows":
            gl_api.add("opengl")
        elif self.settings.os in ["iOS", "tvOS", "watchOS"]:
            gl_api.add("gles2")

        if len(gl_api) == 0:
            raise ConanInvalidConfiguration("No GL API selected")

        return list(gl_api)

    def _get_gl_platform(self):
        gl_platform = set()
        if self.options.get_safe("with_egl"):
            gl_platform.add("egl")
        if self.options.get_safe("with_xorg"):
            gl_platform.add("glx")
        if self.options.get_safe("with_wayland"):
            gl_platform.add("egl")
        if self.settings.os == "Macos":
            gl_platform.add("cgl")
        elif self.settings.os in ["iOS", "tvOS", "watchOS"]:
            gl_platform.add("eagl")
        elif self.settings.os == "Windows":
            gl_platform.add("wgl")

        return list(gl_platform)

    def _get_gl_winsys(self):
        gl_winsys = set()
        if self.options.get_safe("with_egl"):
            gl_winsys.add("egl")
        if self.options.get_safe("with_xorg"):
            gl_winsys.add("x11")
        if self.options.get_safe("with_wayland"):
            gl_winsys.add("wayland")
        if self.settings.os == "Macos":
            gl_winsys.add("cocoa")
        elif self.settings.os == "Windows":
            gl_winsys.add("win32")

        return list(gl_winsys)

    def _get_gl_platform_deps(self):
        gl_platform_deps = set()
        if self.options.get_safe("with_egl"):
            gl_platform_deps.add("egl::egl")

        return list(gl_platform_deps)

    def _get_gl_winsys_deps(self):
        gl_winsys_deps = set()
        if self.options.get_safe("with_xorg"):
            gl_winsys_deps.add("xorg::x11")
            gl_winsys_deps.add("xorg::x11-xcb")
        if self.options.get_safe("with_wayland"):
            gl_winsys_deps.add("wayland::wayland")
            gl_winsys_deps.add("wayland::wayland-client")
            gl_winsys_deps.add("wayland::wayland-cursor")
            gl_winsys_deps.add("wayland::wayland-egl")
            gl_winsys_deps.add("wayland-protocols::wayland-protocols")
        if self.settings.os == "Windows":
            gl_winsys_deps.add("wglext::wglext")
            gl_winsys_deps.add("glext::glext")

        return list(gl_winsys_deps)

    def _get_gl_system_deps(self):
        if self.settings.os == "Windows":
            return ["gdi32"]
        else:
            return []

    def _get_gl_plugin_deps(self):
        gl_plugin_deps = set()
        if self.options.get_safe("gst_base_gl_graphene"):
            gl_plugin_deps.add("graphene::graphene")
        if self.options.get_safe("gst_base_gl_png"):
            gl_plugin_deps.add("libpng::libpng")
        if self.options.get_safe("gst_base_gl_jpeg") == "libjpeg":
            gl_plugin_deps.add("libjpeg::libjpeg")
        elif self.options.get_safe("gst_base_gl_jpeg") == "libjpeg-turbo":
            gl_plugin_deps.add("libjpeg-turbo::libjpeg-turbo")

        if self.options.get_safe("with_xorg"):
            gl_plugin_deps.add("xorg::x11")

        return list(gl_plugin_deps)

    def _validate_gl_config(self):
        if self.options.get_safe("with_egl") and not self.options.get_safe("with_xorg"):
            raise ConanInvalidConfiguration("with_egl requires with_xorg")
        if self.options.get_safe("with_wayland") and not self.options.get_safe("with_egl"):
            raise ConanInvalidConfiguration("with_wayland requires with_egl")

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["auto_features"] = "disabled"
        tc.project_options["default_library"] = "static" # gstreamer-full is only in static
        tc.project_options["gst-full-target-type"] = "static_library"

        # GStreamer subprojects
        tc.project_options["base"] = "enabled" if self.options.with_base else "disabled"
        tc.project_options["good"] = "enabled" if self.options.with_good else "disabled"
        tc.project_options["ugly"] = "enabled" if self.options.with_ugly else "disabled"
        tc.project_options["bad"] = "enabled" if self.options.with_bad else "disabled"
        tc.project_options["libav"] = "enabled" if self.options.with_libav else "disabled"
        tc.project_options["rtsp_server"] = "enabled" if self.options.with_rtsp_server else "disabled"

        # Other options
        tc.project_options["build-tools-source"] = "system" # Use conan's flex and bison
        tc.project_options["orc-source"] = "subproject" # Conan doesn't provide orc

        # Common options
        tc.project_options["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        tc.project_options["orc"] = "enabled" if self.options.with_orc else "disabled"

        tc.project_options["tools"] = "enabled" if self.options.with_tools else "disabled"

        # Enable all plugins by default
        tc.project_options["gst-full-plugins"] = '*'

        tc.subproject_options["gstreamer"] = [{'coretracers': 'enabled' if self.options.with_coretracers else 'disabled'}]

        # Feature options for plugins with no external deps
        if self.options.with_base:
            tc.subproject_options["gst-plugins-base"] = []
            for option in GST_BASE_MESON_OPTIONS:
                tc.subproject_options["gst-plugins-base"].append({option: 'enabled' if self.options.get_safe(f'gst_base_{option}') else 'disabled'})
            for option in GST_BASE_MESON_OPTIONS_WITH_EXT_DEPS:
                tc.subproject_options["gst-plugins-base"].append({option: 'enabled' if self.options.get_safe(f'gst_base_{option}') else 'disabled'})

            tc.subproject_options["gst-plugins-base"].append({'audioresample_format': str(self.options.gst_base_audioresample_format)})
            if self.options.gst_base_gl:
                for option in GST_BASE_MESON_OPTIONS_GL:
                    mod_option = option.replace("gl_", "gl-")
                    tc.subproject_options["gst-plugins-base"].append({mod_option: 'enabled' if self.options.get_safe(f'gst_base_{option}') else 'disabled'})
                if self.options.gst_base_gl_jpeg != "disabled":
                    tc.subproject_options["gst-plugins-base"].append({'gl-jpeg': 'enabled'})

                tc.subproject_options["gst-plugins-base"].append({'gl_api': self._get_gl_api()})
                tc.subproject_options["gst-plugins-base"].append({'gl_platform': self._get_gl_platform()})
                tc.subproject_options["gst-plugins-base"].append({'gl_winsys': self._get_gl_winsys()})

        if self.options.with_good:
            tc.subproject_options["gst-plugins-good"] = []
            for option in GST_GOOD_MESON_OPTIONS:
                tc.subproject_options["gst-plugins-good"].append({option: 'enabled' if self.options.get_safe(f'gst_good_{option}') else 'disabled'})

        if self.options.with_bad:
            tc.subproject_options["gst-plugins-bad"] = []
            for option in GST_BAD_MESON_OPTIONS:
                tc.subproject_options["gst-plugins-bad"].append({option: 'enabled' if self.options.get_safe(f'gst_bad_{option}') else 'disabled'})

        if self.options.with_ugly:
            tc.subproject_options["gst-plugins-ugly"] = []
            for option in GST_UGLY_MESON_OPTIONS:
                tc.subproject_options["gst-plugins-ugly"].append({option: 'enabled' if self.options.get_safe(f'gst_ugly_{option}') else 'disabled'})

        if self.options.with_rtsp_server:
            tc.subproject_options["gst-rtsp-server"] = []
            for option in GST_RTSP_SERVER_MESON_OPTIONS:
                tc.subproject_options["gst-rtsp-server"].append({option: 'enabled' if self.options.get_safe(f'gst_rtsp_server_{option}') else 'disabled'})

        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

        tc = VirtualBuildEnv(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "gstreamer-1.0", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_id(self):
        if not self.info.options.get_safe("with_xorg"):
            self.info.options.rm_safe('gst_base_x11')
            self.info.options.rm_safe('gst_base_xshm')
            self.info.options.rm_safe('gst_base_xi')
            self.info.options.rm_safe('gst_base_ximage')
            self.info.options.rm_safe('gst_base_xvimage')

        if not self.info.options.with_base:
            for option in GST_BASE_MESON_OPTIONS:
                delattr(self.info.options, f'gst_base_{option}')
            for option in GST_BASE_MESON_OPTIONS_WITH_EXT_DEPS:
                delattr(self.info.options, f'gst_base_{option}')
            for option in GST_BASE_MESON_OPTIONS_GL:
                delattr(self.info.options, f'gst_base_{option}')
            delattr(self.info.options, "gst_base_gl_jpeg")
        if not self.info.options.with_good:
            for option in GST_GOOD_MESON_OPTIONS:
                delattr(self.info.options, f'gst_good_{option}')
        if not self.info.options.with_bad:
            for option in GST_BAD_MESON_OPTIONS:
                delattr(self.info.options, f'gst_bad_{option}')
        if not self.info.options.with_ugly:
            for option in GST_UGLY_MESON_OPTIONS:
                delattr(self.info.options, f'gst_ugly_{option}')
        if not self.info.options.with_rtsp_server:
            for option in GST_RTSP_SERVER_MESON_OPTIONS:
                delattr(self.info.options, f'gst_rtsp_server_{option}')

    def _add_components(self, name, requires, system_libs = None):
        self.cpp_info.components[name].libs = [name]
        self.cpp_info.components[name].libdirs = [os.path.join(self.package_folder, "lib", "gstreamer-1.0")]
        self.cpp_info.components[name].requires = requires
        self.cpp_info.components[name].defines = ["GST_STATIC_COMPILATION"]
        if system_libs:
            self.cpp_info.components[name].system_libs = system_libs
        self.libraries.append(name)

    def _quick(self, lib, is_gst_lib = True):
        GST_LIB_PATH = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        LIB_PATH = os.path.join(self.package_folder, "lib")

        if f"gst{lib}" not in self.cpp_info.components:
            self.cpp_info.components[f"gst{lib}"].libs = [f"gst{lib}"]
            self.cpp_info.components[f"gst{lib}"].libdirs = [GST_LIB_PATH if is_gst_lib else LIB_PATH]
            self.libraries.append(f"gst{lib}")

    def _add_plugin_components(self, lib, requires = [], system_libs = []):
        self.cpp_info.components[f"gst{lib}"].libs = [f"gst{lib}"]
        self.cpp_info.components[f"gst{lib}"].libdirs = [os.path.join(self.package_folder, "lib", "gstreamer-1.0")]
        self.cpp_info.components[f"gst{lib}"].requires = requires
        self.cpp_info.components[f"gst{lib}"].system_libs = system_libs
        self.cpp_info.components[f"gst{lib}"].defines = ["GST_STATIC_COMPILATION"]
        self.libraries.append(f"gst{lib}")

    def _add_library_components(self, lib, requires = [], system_libs = []):
        self.cpp_info.components[f"gstreamer-{lib}-1.0"].libs = [f"gst{lib}-1.0"]
        self.cpp_info.components[f"gstreamer-{lib}-1.0"].libdirs = [os.path.join(self.package_folder, "lib")]
        self.cpp_info.components[f"gstreamer-{lib}-1.0"].includedirs = [os.path.join(self.package_folder, "include", "gstreamer-1.0")]
        self.cpp_info.components[f"gstreamer-{lib}-1.0"].requires = requires
        self.cpp_info.components[f"gstreamer-{lib}-1.0"].system_libs = system_libs
        self.cpp_info.components[f"gstreamer-{lib}-1.0"].defines = ["GST_STATIC_COMPILATION"]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gstreamer-full-1.0")
        self.cpp_info.set_property("cmake_target_name", "gstreamer-full-1.0::gstreamer-full-1.0")

        if self.options.with_orc:
            orc_dep = ["orc"]
            self.cpp_info.components["orc"].libs = ["orc-0.4"]
            self.cpp_info.components["orc"].includedirs = [os.path.join(self.package_folder, "include", "orc-0.4")]
            self.cpp_info.components["orc"].set_property("cmake_target_name", "orc")
        else:
            orc_dep = []

        self.libraries = []
        self.cpp_info.components["gstreamer-1.0"].libs = ["gstreamer-1.0"]
        self.cpp_info.components["gstreamer-1.0"].libdirs = [os.path.join(self.package_folder, "lib")]
        self.cpp_info.components["gstreamer-1.0"].includedirs = [os.path.join(self.package_folder, "include", "gstreamer-1.0")]
        self.cpp_info.components["gstreamer-1.0"].requires = ["glib::glib-2.0", "glib::gobject-2.0", "glib::gmodule-2.0"]
        self.cpp_info.components["gstreamer-1.0"].defines = ["GST_STATIC_COMPILATION"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gstreamer-1.0"].system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["gstreamer-1.0"].system_libs.append("ws2_32")
        elif self.settings.os == "Macos":
            self.cpp_info.components["gstreamer-1.0"].system_libs.append("Cocoa")
        elif self.settings.os == "Android":
            self.cpp_info.components["gstreamer-1.0"].system_libs.append("log")

        gst_dep = ["gstreamer-1.0"]
        libm = ["m"] if self.settings.os in ["Linux", "FreeBSD"] else []
        winsock2 = ["ws2_32"] if self.settings.os == "Windows" else []
        cocoa = ["Cocoa"] if self.settings.os == "Macos" else []
        log = ["log"] if self.settings.os == "Android" else []
        zlib_dep = ["zlib::zlib"]
        gio_dep = ["glib::gio-2.0"]
        gmodule_dep = ["glib::gmodule-2.0"]

        self._add_library_components("base", gst_dep)
        self._add_library_components("controller", gst_dep, libm)
        self._add_library_components("net", gst_dep, libm)

        gst_base_dep = ["gstreamer-base-1.0"]
        gst_controller_dep = ["gstreamer-controller-1.0"]
        gst_net_dep = ["gstreamer-net-1.0"]

        if self.options.with_base:
            #self._add_library_components("plugins-base", ["libdrm::libdrm"] + gst_dep)
            self._add_library_components("allocators", ["libdrm::libdrm"] + gst_dep); allocators_dep = ["gstreamer-allocators-1.0"]
            self._add_library_components("app", gst_base_dep); app_dep = ["gstreamer-app-1.0"]
            self._add_library_components("tag", gst_base_dep + zlib_dep, libm); tag_dep = ["gstreamer-tag-1.0"]
            self._add_library_components("audio", tag_dep + gst_base_dep + orc_dep, libm); audio_dep = ["gstreamer-audio-1.0"]
            self._add_library_components("video", gst_base_dep + orc_dep, libm); video_dep = ["gstreamer-video-1.0"]
            self._add_library_components("fft", gst_dep, libm); fft_dep = ["gstreamer-fft-1.0"]
            self._add_library_components("riff", audio_dep + tag_dep); riff_dep = ["gstreamer-riff-1.0"]
            self._add_library_components("rtp", audio_dep + gst_base_dep); rtp_dep = ["gstreamer-rtp-1.0"]
            self._add_library_components("pbutils", video_dep + audio_dep + tag_dep); pbutils_dep = ["gstreamer-pbutils-1.0"]
            self._add_library_components("sdp", rtp_dep + gst_dep + gio_dep + pbutils_dep); sdp_dep = ["gstreamer-sdp-1.0"]
            self._add_library_components("rtsp", gst_base_dep + gst_dep + gio_dep + sdp_dep, libm + winsock2); rtsp_dep = ["gstreamer-rtsp-1.0"]

            for lib in GST_BASE_MESON_OPTIONS:
                # drm doesn't genereate a lib, it adds a dummy drm driver in gstreamer-allocators
                # gio-typefind is to add glib2::gio-2.0 to typefindfunctions
                # xi and xshm doesn't generate a lib
                if lib in ["drm", "gio-typefinder", "xi", "xshm"]: continue
                if self.options.get_safe(f'gst_base_{lib}'):
                    # typefind lib's name is typefindfunctions
                    if lib is "typefind": lib = "typefindfunctions"
                    if lib is "debugutils": lib = "basedebug"
                    self._add_plugin_components(lib)

            self.cpp_info.components['adder'].requires = audio_dep + orc_dep
            self.cpp_info.components['app'].requires = gst_base_dep + app_dep + tag_dep
            self.cpp_info.components['audioconvert'].requires = audio_dep + gst_base_dep
            self.cpp_info.components['audiomixer'].requires = audio_dep + gst_base_dep + orc_dep
            self.cpp_info.components['audiorate'].requires = audio_dep + gst_base_dep
            self.cpp_info.components['audioresample'].requires = audio_dep + gst_base_dep
            self.cpp_info.components['audioresample'].system_libs = libm
            self.cpp_info.components['audiotestsrc'].requires = audio_dep + gst_base_dep
            self.cpp_info.components['audiotestsrc'].system_libs = libm
            self.cpp_info.components['compositor'].requires = video_dep + gst_base_dep + orc_dep
            self.cpp_info.components['compositor'].system_libs = libm
            self.cpp_info.components['basedebug'].requires = gst_dep + gst_base_dep + video_dep
            self.cpp_info.components['dsd'].requires = audio_dep + gst_base_dep
            self.cpp_info.components['encoding'].requires = pbutils_dep + video_dep + gst_base_dep
            self.cpp_info.components['gio'].requires = gst_base_dep + gio_dep
            self.cpp_info.components['overlaycomposition'].requires = video_dep
            self.cpp_info.components['pbtypes'].requires = video_dep
            self.cpp_info.components['playback'].requires = audio_dep + video_dep + pbutils_dep + tag_dep
            self.cpp_info.components['rawparse'].requires = gst_base_dep + video_dep + audio_dep
            self.cpp_info.components['subparse'].requires = gst_base_dep
            self.cpp_info.components['tcp'].requires = gst_base_dep + gst_net_dep + gio_dep
            self.cpp_info.components['typefindfunctions'].requires = pbutils_dep + gst_base_dep
            self.cpp_info.components['videoconvertscale'].requires = video_dep + gst_dep + gst_base_dep
            self.cpp_info.components['videorate'].requires = video_dep
            self.cpp_info.components['videotestsrc'].requires = video_dep + gst_dep + gst_base_dep + orc_dep
            self.cpp_info.components['videotestsrc'].system_libs = libm
            self.cpp_info.components['volume'].requires = audio_dep + gst_dep + gst_base_dep + orc_dep

            if self.options.get_safe('gst_base_typefind') and self.options.get_safe('gst_base_gio-typefinder'):
                self.cpp_info.components["gsttypefindfunctions"].requires.append("glib::gio-2.0")

            # Base pulgins with external dependencies
            if self.options.get_safe('gst_base_alsa'):
                self._add_plugin_components("alsa", ["libalsa::libalsa"] + audio_dep + tag_dep + gst_dep + gst_base_dep)

            if self.options.get_safe('gst_base_ogg'):
                self._add_plugin_components("ogg", ["ogg::ogg"] + audio_dep + pbutils_dep + tag_dep + riff_dep + gst_dep + gst_base_dep)

            if self.options.get_safe('gst_base_opus'):
                self._add_plugin_components("opus", ["opus::opus"] + pbutils_dep + tag_dep + audio_dep + gst_dep + gst_base_dep, libm)

            if self.options.get_safe('gst_base_pango'):
                self._add_plugin_components("pango", ["pango::pangocairo"] + video_dep + gst_dep + gst_base_dep, libm)

            if self.options.get_safe('gst_base_theora'):
                self._add_plugin_components("theora", ["theora::theora"] + video_dep + tag_dep + gst_dep + gst_base_dep)

            if self.options.get_safe('gst_base_vorbis'):
                self._add_plugin_components("vorbis", ["vorbis::vorbis"] + audio_dep + tag_dep + gst_dep + gst_base_dep)
                # TODO: Add gstivorbisdec once tremor is supported

            if self.options.get_safe('gst_base_x11'):
                extra_libs = ["xorg::x11"]
                if self.options.get_safe('gst_base_xshm'):
                    extra_libs.append("xorg::xext")
                if self.options.get_safe('gst_base_xi'):
                    extra_libs.append("xorg::xi")
                self._add_plugin_components("ximagesink", video_dep + gst_base_dep + gst_dep + extra_libs + ["xorg::x11"])
                if self.options.get_safe('gst_base_xvideo'):
                    self._add_plugin_components("xvimagesink", video_dep + gst_base_dep + gst_dep + extra_libs + ["xorg::xv"], libm)

            gl_lib_deps = ["opengl::opengl"]
            gl_misc_deps = []

            if getattr(self.options, 'gst_base_gl'):
                self._add_library_components("gl", gst_base_dep + video_dep + allocators_dep + gmodule_dep + gl_lib_deps + self._get_gl_platform_deps() + self._get_gl_winsys_deps() + gl_misc_deps); gstgl_dep = ["gstreamer-gl-1.0"]
                #self._add_library_components("gl-prototypes", gstgl_dep + gl_lib_deps)

#                if self.options.get_safe("with_xorg"):
#                    self._add_library_components("gl-x11", gstgl_dep, ["xorg::x11", "xorg::x11-xcb"])
#
#                if self.options.get_safe("with_wayland"):
#                    self._add_library_components("gl-wayland", gstgl_dep)
#
#                if self.options.get_safe("with_egl"):
#                    self._add_library_components("gl-egl", gstgl_dep)

                self._add_plugin_components("opengl", gstgl_dep + video_dep + gl_lib_deps + self._get_gl_plugin_deps(), libm)

        if self.options.with_good:
            for lib in GST_GOOD_MESON_OPTIONS:
                if self.options.get_safe(f'gst_good_{lib}'):
                    if lib is "alpha":
                        self._add_plugin_components("alpha", video_dep + gst_dep, libm)
                        self._add_plugin_components("alphacolor", video_dep + gst_dep)
                    if lib is "debugutils":
                        self._quick("navigationtest")
                        self._quick("debug")
                    elif lib is "law":
                        self._quick("alaw")
                        self._quick("mulaw")
                    elif lib is "flx": self._quick("flxdec")
                    elif lib is "y4m": self._quick("y4menc")
                    else:
                        self._quick(lib)

        if self.options.with_bad:
            for lib in GST_BAD_MESON_OPTIONS:
                if self.options.get_safe(f'gst_bad_{lib}'):
                    if lib is "camerabin2": lib = "camerabin"
                    elif lib is "debugutils": lib =  "debugutilsbad"
                    elif lib is "librfb": lib = "rfbsrc"
                    elif lib is "mpegdemux": lib = "mpegpsdemux"
                    elif lib is "onvif": lib = "rtponvif"
                    elif lib is "rawparse": lib = "legacyrawparse"
                    elif lib is "rtp": lib = "rtpmanagerbad"
                    elif lib is "videofilters": lib = "videofiltersbad"
                    elif lib is "videoparsers":lib = "videoparsersbad"
                    elif lib is "sdp": lib = "sdpelem"
                    elif lib is "y4m": lib = "y4mdec"
                    self.cpp_info.components[f"gst{lib}"].libs = [f"gst{lib}"]
                    self.cpp_info.components[f"gst{lib}"].libdirs = [os.path.join(self.package_folder, "lib", "gstreamer-1.0")]
                    self.libraries.append(f"gst{lib}")

                    if lib is "camerabin":
                            self._quick("basecamerabinsrc-1.0", False)
                            self._quick("photography-1.0", False)
                            self.cpp_info.components[f"gst{lib}"].requires = ["gstbasecamerabinsrc-1.0"]
                            self.cpp_info.components[f"gst{lib}"].requires = ["gstphotography-1.0"]
                    if lib is "insertbin":
                        self._quick("insertbin-1.0", False)
                        self.cpp_info.components[f"gst{lib}"].requires = ["gstinsertbin-1.0"]
                    if lib in ["jpegformat", "videoparsersbad"]:
                            self._quick("codecparsers-1.0", False)
                            self.cpp_info.components[f"gst{lib}"].requires = ["gstcodecparsers-1.0"]
                    if lib in ["mpegtsdemux", "mpegtsmux"]:
                        self._quick("mpegts-1.0", False)
                        self.cpp_info.components[f"gst{lib}"].requires = ["gstmpegts-1.0"]
                    if lib is "mse":
                            self._quick("mse-1.0", False)
                            self.cpp_info.components[f"gst{lib}"].requires = ["gstmse-1.0"]

                    if lib is "unixfd":
                        self.cpp_info.components[f"gst{lib}"].requires = ["gstallocators-1.0"]

        if self.options.with_ugly:
            for lib in GST_UGLY_MESON_OPTIONS:
                if self.options.get_safe(f'gst_ugly_{lib}'):
                        if lib is "asfdemux": lib = "asf"
                        self._quick(lib)

        if self.options.with_libav:
            libav_deps = ["ffmpeg::avfilter", "ffmpeg::avformat", "ffmpeg::avcodec", "ffmpeg::avutil"]
            libav_deps.extend(gst_dep + audio_dep + video_dep + gst_base_dep)
            self._add_plugin_components("libav", libav_deps)

        if self.options.with_rtsp_server:
            self._quick('rtspserver-1.0', False)

            for lib in GST_RTSP_SERVER_MESON_OPTIONS:
                if self.options.get_safe(f'gst_rtsp_server_{lib}'):
                        self._quick(lib)
                        if lib is "rtspclientsink":
                            self.cpp_info.components["gstrtspclientsink"].requires = ["gstrtspserver-1.0"]

        self.cpp_info.components["gstcoreelements"].set_property("cmake_target_name", "gstreamer-full-1.0::gstcoreelements")
        self.cpp_info.components["gstcoreelements"].libs = ["gstcoreelements"]
        self.cpp_info.components["gstcoreelements"].libdirs = [os.path.join(self.package_folder, "lib", "gstreamer-1.0")]
        self.cpp_info.components["gstcoreelements"].includedirs = [os.path.join(self.package_folder, "include", "gstreamer-1.0")]
        self.cpp_info.components["gstcoreelements"].requires = ["glib::gobject-2.0", "glib::glib-2.0", "gstreamer-1.0"]
        self.libraries.append("gstcoreelements")

        if self.options.with_coretracers:
            self.cpp_info.components["gstcoretracers"].set_property("cmake_target_name", "gstreamer-full-1.0::gstcoretracers")
            self.cpp_info.components["gstcoretracers"].libs = ["gstcoretracers"]
            self.cpp_info.components["gstcoretracers"].libdirs = [os.path.join(self.package_folder, "lib", "gstreamer-1.0")]
            self.cpp_info.components["gstcoretracers"].includedirs = [os.path.join(self.package_folder, "include", "gstreamer-1.0")]
            self.cpp_info.components["gstcoretracers"].requires = ["glib::gobject-2.0", "glib::glib-2.0", "gstreamer-1.0"]
            self.libraries.append("gstcoretracers")

        self.cpp_info.components["gstreamer-full-1.0"].set_property("cmake_target_name", "gstreamer-full-1.0::gstreamer-full-1.0")
        self.cpp_info.components["gstreamer-full-1.0"].libs = ["gstreamer-full-1.0"]
        self.cpp_info.components["gstreamer-full-1.0"].libdirs = [os.path.join(self.package_folder, "lib")]
        self.cpp_info.components["gstreamer-full-1.0"].includedirs = [os.path.join(self.package_folder, "include", "gstreamer-1.0")]
        self.cpp_info.components["gstreamer-full-1.0"].requires = ["glib::glib-2.0", "glib::gobject-2.0", "glib::gmodule-2.0"]
        self.cpp_info.components["gstreamer-full-1.0"].defines = ["GST_STATIC_COMPILATION"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gstreamer-full-1.0"].system_libs.append("m")
            self.cpp_info.components["gstreamer-full-1.0"].system_libs.append("pthread")

        self.cpp_info.components["gstreamer-full-1.0"].requires.extend(self.libraries)

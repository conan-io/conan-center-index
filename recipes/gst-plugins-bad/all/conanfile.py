import glob
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.files import chdir, copy, get, rm, rmdir, rename, export_conandata_patches, apply_conandata_patches, \
    replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, check_min_vs, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2.4"

class GStPluginsBadConan(ConanFile):
    name = "gst-plugins-bad"
    description = "A set of plugins for GStreamer that may pose distribution problems."
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_aom": [True, False],
        "with_bz2": [True, False],
        "with_faac": [True, False],
        "with_fdk_aac": [True, False],
        "with_google_cloud_storage": [True, False],
        "with_gtk": [True, False],
        "with_lcms": [True, False],
        "with_libcurl": [True, False],
        "with_libdrm": [True, False],
        "with_libdc1394": [True, False],
        "with_libde265": [True, False],
        "with_libssh2": [True, False],
        "with_libxml2": [True, False],
        "with_modplug": [True, False],
        "with_nice": [True, False],
        "with_onnx": [True, False],
        "with_openal": [True, False],
        "with_opencv": [True, False],
        "with_openexr": [True, False],
        "with_openh264": [True, False],
        "with_openjpeg": [True, False],
        "with_openni2": [True, False],
        "with_opus": [True, False],
        "with_pango": [True, False],
        "with_qt": [True, False],
        "with_rsvg": [True, False],
        "with_sctp": [True, False],
        "with_sndfile": [True, False],
        "with_soundtouch": [True, False],
        "with_srt": [True, False],
        "with_srtp": [True, False],
        "with_ssl": ["openssl", False],
        "with_svtav1": [True, False],
        "with_tinyalsa": [True, False],
        "with_voamrwbenc": [True, False],
        "with_vulkan": [True, False],
        "with_webp": [True, False],
        "with_wildmidi": [True, False],
        "with_x265": [True, False],
        "with_zbar": [True, False],
        "with_zxing": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_aom": True,
        "with_bz2": True,
        "with_faac": True,
        "with_fdk_aac": True,
        "with_google_cloud_storage": True,
        "with_gtk": True,
        "with_lcms": True,
        "with_libcurl": True,
        "with_libdrm": True,
        "with_libdc1394": True,
        "with_libde265": True,
        "with_libssh2": True,
        "with_libxml2": True,
        "with_modplug": True,
        "with_nice": True,
        "with_onnx": False,
        "with_openal": True,
        "with_opencv": True,
        "with_openexr": True,
        "with_openh264": True,
        "with_openjpeg": True,
        "with_openni2": True,
        "with_opus": True,
        "with_pango": True,
        "with_qt": False,
        "with_rsvg": True,
        "with_sctp": True,
        "with_srt": True,
        "with_srtp": True,
        "with_sndfile": True,
        "with_soundtouch": True,
        "with_ssl": "openssl",
        "with_svtav1": True,
        "with_tinyalsa": True,
        "with_voamrwbenc": True,
        "with_vulkan": True,
        "with_webp": True,
        "with_wildmidi": True,
        "with_x265": True,
        "with_zbar": True,
        "with_zxing": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_libcurl:
            del self.options.with_libssh2
        self.options["gstreamer"].shared = self.options.shared
        self.options["gst-plugins-base"].shared = self.options.shared

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"gstreamer/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires(f"gst-plugins-base/{self.version}", transitive_headers=True, transitive_libs=True)

        if self.options.with_aom:
            self.requires("libaom-av1/3.8.0")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_faac:
            self.requires("faac/1.30")
        if self.options.with_fdk_aac:
            self.requires("libfdk_aac/2.0.3")
        if self.options.with_google_cloud_storage:
            self.requires("google-cloud-cpp/2.28.0")
        if self.options.with_gtk:
            # Only GTK 3 is supported
            self.requires("gtk/3.24.43")
        if self.options.with_libcurl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.with_libdrm:
            self.requires("libdrm/2.4.119")
        if self.options.with_libdc1394:
            self.requires("libdc1394/2.2.7")
        # if self.options.with_libqrencode:
        #     self.requires("libqrencode/4.1.1")
        if self.options.with_libde265:
            self.requires("libde265/1.0.15")
        if self.options.get_safe("with_libssh2"):
            self.requires("libssh2/1.11.1")
        if self.options.with_libxml2:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.with_lcms:
            self.requires("lcms/2.16")
        if self.options.with_modplug:
            self.requires("libmodplug/0.8.9.0")
        if self.options.with_nice:
            self.requires("libnice/0.1.21")
        if self.options.with_onnx:
            self.requires("onnxruntime/1.18.1")
        if self.options.with_openal:
            self.requires("openal-soft/1.22.2")
        if self.options.with_opencv:
            # Only < 3.5.0 is supported. 'contrib' is required for opencv_tracking.
            self.requires("opencv/3.4.20", options={"contrib": True})
        if self.options.with_openexr:
            # 3.x is not supported
            self.requires("openexr/2.5.7")
        if self.options.with_openh264:
            self.requires("openh264/2.5.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.2")
        if self.options.with_openni2:
            self.requires("openni2/2.2.0.33")
        if self.options.with_opus:
            self.requires("opus/1.4")
        if self.options.with_pango:
            self.requires("pango/1.54.0")
        if self.options.with_qt:
            self.requires("qt/[>=6.7 <7]", options={
                "qtdeclarative": True,
                "qtshadertools": True,
                "qttools": can_run(self)
            })
        if self.options.with_rsvg:
            self.requires("librsvg/2.40.21")
        if self.options.with_sctp:
            self.requires("usrsctp/0.9.5.0")
        if self.options.with_sndfile:
            self.requires("libsndfile/1.2.2")
        if self.options.with_soundtouch:
            self.requires("soundtouch/2.3.3")
        if self.options.with_srt:
            self.requires("srt/1.5.3")
        if self.options.with_srtp:
            self.requires("libsrtp/2.6.0")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_svtav1:
            self.requires("libsvtav1/2.2.1")
        if self.options.with_tinyalsa:
            self.requires("tinyalsa/2.0.0")
        if self.options.with_voamrwbenc:
            self.requires("vo-amrwbenc/0.1.3")
        if self.options.with_vulkan:
            self.requires("vulkan-loader/1.3.290.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.with_wildmidi:
            self.requires("wildmidi/0.4.5")
        if self.options.with_x265:
            self.requires("libx265/3.4")
        if self.options.with_zbar:
            self.requires("zbar/0.23.92")
        if self.options.with_zxing:
            self.requires("zxing-cpp/2.2.1")

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

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        self.tool_requires("glib/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.options.with_vulkan:
            self.tool_requires("shaderc/2024.1")
        if self.options.with_qt and not can_run(self):
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

        def feature(value):
            return "enabled" if value else "disabled"

        if self.settings.get_safe("compiler.runtime"):
            tc.properties["b_vscrt"] = str(self.settings.compiler.runtime).lower()

        # Feature options for plugins without external deps
        tc.project_options["accurip"] = "enabled"
        tc.project_options["adpcmdec"] = "enabled"
        tc.project_options["adpcmenc"] = "enabled"
        tc.project_options["aiff"] = "enabled"
        tc.project_options["analyticsoverlay"] = feature(self.options.with_pango)
        tc.project_options["asfmux"] = "enabled"
        tc.project_options["audiobuffersplit"] = "enabled"
        tc.project_options["audiofxbad"] = "enabled"
        tc.project_options["audiolatency"] = "enabled"
        tc.project_options["audiomixmatrix"] = "enabled"
        tc.project_options["audiovisualizers"] = "enabled"
        tc.project_options["autoconvert"] = "enabled"
        tc.project_options["bayer"] = "enabled"
        tc.project_options["camerabin2"] = "enabled"
        tc.project_options["codec2json"] = "disabled"  # json-glib-1.0
        tc.project_options["codecalpha"] = "enabled"
        tc.project_options["codectimestamper"] = "enabled"
        tc.project_options["coloreffects"] = "enabled"
        tc.project_options["debugutils"] = "enabled"
        tc.project_options["dvbsubenc"] = "enabled"
        tc.project_options["dvbsuboverlay"] = "enabled"
        tc.project_options["dvdspu"] = "enabled"
        tc.project_options["faceoverlay"] = "enabled"
        tc.project_options["festival"] = "enabled"
        tc.project_options["fieldanalysis"] = "enabled"
        tc.project_options["freeverb"] = "enabled"
        tc.project_options["frei0r"] = "enabled"
        tc.project_options["gaudieffects"] = "enabled"
        tc.project_options["gdp"] = "enabled"
        tc.project_options["geometrictransform"] = "enabled"
        tc.project_options["id3tag"] = "enabled"
        tc.project_options["insertbin"] = "enabled"
        tc.project_options["inter"] = "enabled"
        tc.project_options["interlace"] = "enabled"
        tc.project_options["ivfparse"] = "enabled"
        tc.project_options["ivtc"] = "enabled"
        tc.project_options["jp2kdecimator"] = "enabled"
        tc.project_options["jpegformat"] = "enabled"
        tc.project_options["librfb"] = "enabled"
        tc.project_options["midi"] = "enabled"
        tc.project_options["mpegdemux"] = "enabled"
        tc.project_options["mpegpsmux"] = "enabled"
        tc.project_options["mpegtsdemux"] = "enabled"
        tc.project_options["mpegtsmux"] = "enabled"
        tc.project_options["mse"] = "enabled"
        tc.project_options["mxf"] = "enabled"
        tc.project_options["netsim"] = "enabled"
        tc.project_options["onvif"] = "enabled"
        tc.project_options["pcapparse"] = "enabled"
        tc.project_options["pnm"] = "enabled"
        tc.project_options["proxy"] = "enabled"
        tc.project_options["rawparse"] = "enabled"
        tc.project_options["removesilence"] = "enabled"
        tc.project_options["rist"] = "enabled"
        tc.project_options["rtmp2"] = "enabled"
        tc.project_options["rtp"] = "enabled"
        tc.project_options["sdp"] = "enabled"
        tc.project_options["segmentclip"] = "enabled"
        tc.project_options["siren"] = "enabled"
        tc.project_options["smooth"] = "enabled"
        tc.project_options["speed"] = "enabled"
        tc.project_options["subenc"] = "enabled"
        tc.project_options["switchbin"] = "enabled"
        tc.project_options["timecode"] = "enabled"
        tc.project_options["unixfd"] = "enabled"
        tc.project_options["videofilters"] = "enabled"
        tc.project_options["videoframe_audiolevel"] = "enabled"
        tc.project_options["videoparsers"] = "enabled"
        tc.project_options["videosignal"] = "enabled"
        tc.project_options["vmnc"] = "enabled"
        tc.project_options["y4m"] = "enabled"

        # Feature options for libraries that need external deps
        tc.project_options["opencv"] = feature(self.options.with_opencv)

        # Feature options for optional deps in plugins
        # option('drm', type : 'feature', value : 'auto', description: 'libdrm support in the GstVA library')
        # option('udev', type : 'feature', value : 'auto', description: 'gudev support in the new VA-API plugin')
        # option('wayland', type : 'feature', value : 'auto', description : 'Wayland plugin/library, support in the Vulkan plugin')
        # option('x11', type : 'feature', value : 'auto', description : 'X11 support in Vulkan, GL and rfb plugins')

        # Feature options for plugins that need external deps
        tc.project_options["aes"] = feature(self.options.with_ssl == "openssl")
        tc.project_options["aja"] = "disabled"  # libajantv2
        tc.project_options["amfcodec"] =  feature(self.settings == "Windows")
        tc.project_options["androidmedia"] = feature(self.settings.os == "Android")
        tc.project_options["aom"] = feature(self.options.with_aom)
        tc.project_options["applemedia"] = feature(is_apple_os(self))
        tc.project_options["asio"] = "disabled"  # proprietary
        tc.project_options["assrender"] = "disabled"  # libass
        tc.project_options["avtp"] = "disabled"  # avtp
        tc.project_options["bluez"] = "disabled"  # bluez
        tc.project_options["bs2b"] = "disabled"  # libbs2b
        tc.project_options["bz2"] = feature(self.options.with_bz2)
        tc.project_options["chromaprint"] = "disabled"  # libchromaprint
        tc.project_options["closedcaption"] = feature(self.options.with_pango)
        tc.project_options["colormanagement"] = feature(self.options.with_lcms)
        tc.project_options["curl"] = feature(self.options.with_libcurl)
        tc.project_options["curl-ssh2"] = feature(self.options.with_libcurl and self.options.with_libssh2)
        tc.project_options["d3d11"] = feature(self.settings.os == "Windows")
        tc.project_options["d3d12"] = feature(self.settings.os == "Windows")
        tc.project_options["d3dvideosink"] = feature(self.settings.os == "Windows")
        tc.project_options["dash"] = feature(self.options.with_libxml2)
        tc.project_options["dc1394"] = feature(self.options.with_libdc1394)
        tc.project_options["decklink"] = "enabled"  # only system dependencies
        tc.project_options["directfb"] = "disabled"  # directfb
        tc.project_options["directshow"] = feature(is_msvc(self))
        tc.project_options["directsound"] = feature(self.settings.os == "Windows")
        tc.project_options["dtls"] = feature(self.options.with_ssl == "openssl")
        tc.project_options["dts"] = "disabled"  # libdca
        tc.project_options["dvb"] = feature(self.settings.os == "Linux")
        tc.project_options["dwrite"] = feature(self.settings.os == "Windows")
        tc.project_options["faac"] = feature(self.options.with_faac)
        tc.project_options["faad"] = "disabled"  # faad2
        tc.project_options["fbdev"] = feature(self.settings.os == "Linux")
        tc.project_options["fdkaac"] = feature(self.options.with_fdk_aac)
        tc.project_options["flite"] = "disabled"  # flite
        tc.project_options["fluidsynth"] = "disabled"  # fluidsynth
        tc.project_options["gl"] = feature(self.dependencies["gst-plugins-base"].options.with_gl)
        tc.project_options["gme"] = "disabled"  # gme
        tc.project_options["gs"] = feature(self.options.with_google_cloud_storage)
        tc.project_options["gsm"] = "disabled"  # libgsm1
        tc.project_options["gtk3"] = feature(self.options.with_gtk)
        tc.project_options["ipcpipeline"] = "enabled"  # only system dependencies
        tc.project_options["iqa"] = "disabled"  # kornelski/dssim
        tc.project_options["isac"] = "disabled"  # webrtc-audio-coding-1
        tc.project_options["kms"] = feature(self.options.with_libdrm)
        tc.project_options["ladspa"] = "disabled"  # ladspa-sdk
        tc.project_options["ladspa-rdf"] = "disabled"
        tc.project_options["lc3"] = "disabled"  # lc3
        tc.project_options["ldac"] = "disabled"  # ldacbt
        tc.project_options["libde265"] = feature(self.options.with_libde265)
        tc.project_options["lv2"] = "disabled"  # lilv
        tc.project_options["magicleap"] = "disabled"  # proprietary
        tc.project_options["mediafoundation"] = feature(self.settings.os == "Windows")
        tc.project_options["microdns"] = "disabled"  # libmicrodns
        tc.project_options["modplug"] = feature(self.options.with_modplug)
        tc.project_options["mpeg2enc"] = "disabled"  # mjpegtools
        tc.project_options["mplex"] = "disabled"  # mjpegtools
        tc.project_options["msdk"] = "disabled"  # Intel Media SDK or oneVPL SDK
        tc.project_options["musepack"] = "disabled"  # libmpcdec
        tc.project_options["neon"] = "disabled"  # libneon27
        tc.project_options["nvcodec"] = "disabled"  # requires gstcuda
        tc.project_options["onnx"] = feature(self.options.with_onnx)
        tc.project_options["openal"] = feature(self.options.with_openal)
        tc.project_options["openaptx"] = "disabled"  # openaptx
        tc.project_options["openexr"] = feature(self.options.with_openexr)
        tc.project_options["openh264"] = feature(self.options.with_openh264)
        tc.project_options["openjpeg"] = feature(self.options.with_openjpeg)
        tc.project_options["openmpt"] = "disabled"  # openmpt
        tc.project_options["openni2"] = feature(self.options.with_openni2)
        tc.project_options["opensles"] = "disabled"  # opensles
        tc.project_options["opus"] = feature(self.options.with_opus)
        tc.project_options["qroverlay"] = "disabled"  # libqrencode, json-glib-1.0
        tc.project_options["qsv"] = "enabled"  # requires gstd3d11 on Windows, gstva on Linux
        tc.project_options["qt6d3d11"] = feature(self.options.with_qt)
        tc.project_options["resindvd"] = "disabled"  # dvdnav
        tc.project_options["rsvg"] = feature(self.options.with_rsvg)
        tc.project_options["rtmp"] = "disabled"  # librtmp
        tc.project_options["sbc"] = "disabled" # libsbc
        tc.project_options["sctp"] = feature(self.options.with_sctp)
        tc.project_options["shm"] = "enabled"  # only system dependencies
        tc.project_options["smoothstreaming"] = feature(self.options.with_libxml2)
        tc.project_options["sndfile"] = feature(self.options.with_sndfile)
        tc.project_options["soundtouch"] = feature(self.options.with_soundtouch)
        tc.project_options["spandsp"] = "disabled"  # spandsp
        tc.project_options["srt"] = feature(self.options.with_srt)
        tc.project_options["srtp"] = feature(self.options.with_srtp)
        tc.project_options["svtav1"] = feature(self.options.with_svtav1)
        tc.project_options["svthevcenc"] = "disabled"  # svt-hevc
        tc.project_options["teletext"] = "disabled"  # zvbi
        tc.project_options["tinyalsa"] = feature(self.options.with_tinyalsa)
        tc.project_options["transcode"] = "enabled"  # no external deps
        tc.project_options["ttml"] = feature(self.options.with_pango and self.options.with_libxml2)
        tc.project_options["uvcgadget"] = "disabled"  # gudev-1.0
        tc.project_options["uvch264"] = "disabled"  # gudev-1.0
        tc.project_options["v4l2codecs"] = "disabled"  # gudev-1.0
        tc.project_options["va"] = "enabled"  # TODO
        tc.project_options["voaacenc"] = "disabled"  # vo-aacenc
        tc.project_options["voamrwbenc"] = feature(self.options.with_voamrwbenc)
        tc.project_options["vulkan"] = feature(self.options.with_vulkan)
        tc.project_options["wasapi"] = feature(self.settings.os == "Windows")
        tc.project_options["wasapi2"] = feature(self.settings.os == "Windows")
        tc.project_options["webp"] = feature(self.options.with_webp)
        tc.project_options["webrtc"] = feature(self.options.with_nice)
        tc.project_options["webrtcdsp"] = "disabled"  # webrtc-audio-processing-1
        tc.project_options["wic"] = feature(self.settings.os == "Windows")
        tc.project_options["wildmidi"] = feature(self.options.with_wildmidi)
        tc.project_options["win32ipc"] = feature(self.settings.os == "Windows")
        tc.project_options["winks"] = feature(self.settings.os == "Windows")
        tc.project_options["winscreencap"] = feature(self.settings.os == "Windows")
        tc.project_options["wpe"] = "disabled"  # wpe-webkit
        tc.project_options["x265"] = feature(self.options.with_x265)
        tc.project_options["zbar"] = feature(self.options.with_zbar)
        tc.project_options["zxing"] = feature(self.options.with_zxing)

        # D3D11 plugin options
        # option('d3d11-math', type : 'feature', value : 'auto', description : 'Enable DirectX SIMD Math support')
        # option('d3d11-hlsl-precompile', type : 'feature', value : 'auto', description : 'Enable buildtime HLSL compile for d3d11 library/plugin')
        # option('d3d11-wgc', type : 'feature', value : 'auto', description : 'Windows Graphics Capture API support in d3d11 plugin')

        # HLS plugin options
        tc.project_options["hls"] = "enabled"
        tc.project_options["hls-crypto"] = "openssl"

        # SCTP plugin options
        tc.project_options["sctp-internal-usrsctp"] = "disabled"

        # QSV plugin options
        # option('mfx-modules-dir', type: 'string', value : '', description : 'libmfx runtime module dir, linux only')

        # Vulkan plugin options
        tc.project_options["vulkan-video"] = "enabled"

        tc.project_options["gpl"] = "enabled"  # TODO
        tc.project_options["doc"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["nls"] = "disabled"
        tc.project_options["orc"] = "disabled"
        tc.project_options["introspection"] = "disabled"  # TODO

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.set_property("wildmidi", "pkg_config_name", "WildMIDI")
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
        if self.options.shared:
            self.runenv_info.append_path("GST_PLUGIN_PATH", os.path.join(self.package_folder, "lib", "gstreamer-1.0"))

        def _define_plugin(name, extra_requires):
            name = f"gst{name}"
            component = self.cpp_info.components[name]
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
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
                component.defines.append("GST_PLUGINS_GOOD_STATIC")
            return component

        plugins = [
            "accurip",
            "adpcmdec",
            "adpcmenc",
            "aiff",
            "asfmux",
            "audiobuffersplit",
            "audiofxbad",
            "audiolatency",
            "audiomixmatrix",
            "audiovisualizers",
            "autoconvert",
            "bayer",
            "camerabin",
            "codecalpha",
            "coloreffects",
            "debugutilsbad",
            "dvbsubenc",
            "dvbsuboverlay",
            "dvdspu",
            "faceoverlay",
            "festival",
            "fieldanalysis",
            "freeverb",
            "frei0r",
            "gaudieffects",
            "gdp",
            "geometrictransform",
            "id3tag",
            "inter",
            "interlace",
            "ivfparse",
            "ivtc",
            "jp2kdecimator",
            "jpegformat",
            "rfbsrc",
            "midi",
            "mpegpsdemux",
            "mpegpsmux",
            "mpegtsdemux",
            "mpegtsmux",
            "mxf",
            "netsim",
            "rtponvif",
            "pcapparse",
            "pnm",
            "proxy",
            "legacyrawparse",
            "removesilence",
            "rist",
            "rtmp2",
            "rtpmanagerbad",
            "sdpelem",
            "segmentclip",
            "siren",
            "smooth",
            "speed",
            "subenc",
            "switchbin",
            "timecode",
            "transcode",
            "videofiltersbad",
            "videoframe_audiolevel",
            "videoparsersbad",
            "videosignal",
            "vmnc",
            "y4mdec"
        ]

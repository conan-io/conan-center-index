import glob
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run, stdcpp_library
from conan.tools.files import chdir, copy, get, rm, rmdir, rename, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, check_min_vs, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2.0"

class GStPluginsBadConan(ConanFile):
    name = "gst-plugins-bad"
    description = ("GStreamer Bad Plug-ins is a set of plug-ins that aren't up to par compared to the rest."
                   "They might be close to being good quality, but they're missing something - be it a good code review, "
                   "some documentation, a set of tests, a real live maintainer, or some actual wide use.")
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    # Most, but not all, plugins are LGPL. For details, see:
    # https://gitlab.freedesktop.org/gstreamer/gstreamer/-/raw/1.24.10/subprojects/gst-plugins-bad/docs/plugins/gst_plugins_cache.json
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
        "with_json": [True, False],
        "with_lcms": [True, False],
        "with_libcurl": [True, False],
        "with_libdrm": [True, False],
        "with_libdc1394": [True, False],
        "with_libde265": [True, False],
        "with_libqrencode": [True, False],
        "with_libssh2": [True, False],
        "with_libusb": [True, False],
        "with_libudev": [True, False],
        "with_libva": [True, False],
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
        "with_v4l": [True, False],
        "with_vulkan": [True, False],
        "with_wayland": [True, False],
        "with_webp": [True, False],
        "with_wildmidi": [True, False],
        "with_x265": [True, False],
        "with_xorg": [True, False],
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
        "with_json": True,
        "with_lcms": True,
        "with_libcurl": True,
        "with_libdrm": True,
        "with_libdc1394": True,
        "with_libde265": True,
        "with_libqrencode": True,
        "with_libssh2": True,
        "with_libusb": True,
        "with_libudev": True,
        "with_libva": True,
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
        "with_v4l": True,
        "with_vulkan": True,
        "with_wayland": True,
        "with_webp": True,
        "with_wildmidi": True,
        "with_x265": False,  # GPL-licensed
        "with_xorg": True,
        "with_zbar": True,
        "with_zxing": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self.settings not in ["Linux", "FreeBSD"]:
            del self.options.with_xorg
            del self.options.with_wayland

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_libcurl:
            del self.options.with_libssh2
        if self.options.get_safe("with_wayland"):
            self.options.with_libdrm = True
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
        if self.options.with_json:
            self.requires("json-glib/1.10.6")
        if self.options.with_libcurl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.with_libdrm:
            self.requires("libdrm/2.4.119")
        if self.options.with_libdc1394:
            self.requires("libdc1394/2.2.7")
        if self.options.with_libqrencode:
            self.requires("libqrencode/4.1.1")
        if self.options.with_libde265:
            self.requires("libde265/1.0.15")
        if self.options.get_safe("with_libssh2"):
            self.requires("libssh2/1.11.1", options={"shared": True})
        if self.options.with_libusb:
            self.requires("libusb/1.0.26")
        if self.options.with_libudev:
            self.requires("libgudev/238")
        if self.options.with_libva:
            self.requires("libva/2.21.0")
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
        if self.options.with_v4l:
            self.requires("libv4l/1.28.1")
        if self.options.with_vulkan:
            self.requires("vulkan-loader/1.3.290.0")
            if self.options.get_safe("with_wayland") or self.options.get_safe("with_xorg"):
                self.requires("xkbcommon/1.6.0")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.with_wildmidi:
            self.requires("wildmidi/0.4.5")
        if self.options.with_xorg:
            self.requires("xorg/system")
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
        if self.options.get_safe("with_libssh2") and not self.dependencies["libssh2"].options.shared:
            raise ConanInvalidConfiguration("libssh2 must be built as a shared library")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        self.tool_requires("glib/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.options.with_vulkan:
            self.tool_requires("shaderc/2024.1")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland-protocols/1.33")
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
        tc.project_options["codec2json"] = feature(self.options.with_json)
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
        tc.project_options["librfb"] = feature(self.options.get_safe("with_xorg"))
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
        tc.project_options["drm"] = feature(self.options.with_libdrm)
        tc.project_options["udev"] = feature(self.options.with_libudev)
        tc.project_options["wayland"] = feature(self.options.get_safe("with_wayland"))
        tc.project_options["x11"] = feature(self.options.get_safe("with_xorg"))

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
        tc.project_options["dts"] = "disabled"  # libdca (GPL)
        tc.project_options["dvb"] = feature(self.settings.os == "Linux")
        tc.project_options["dwrite"] = feature(self.settings.os == "Windows")
        tc.project_options["faac"] = feature(self.options.with_faac)
        tc.project_options["faad"] = "disabled"  # faad2 (GPL)
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
        tc.project_options["iqa"] = "disabled"  # kornelski/dssim (GPL)
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
        tc.project_options["mpeg2enc"] = "disabled"  # mjpegtools (GPL)
        tc.project_options["mplex"] = "disabled"  # mjpegtools (GPL)
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
        tc.project_options["qroverlay"] = feature(self.options.with_libqrencode and self.options.with_json)
        tc.project_options["qsv"] = "enabled"  # requires gstd3d11 on Windows, gstva on Linux
        tc.project_options["qt6d3d11"] = feature(self.options.with_qt)
        tc.project_options["resindvd"] = "disabled"  # dvdnav (GPL)
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
        tc.project_options["uvcgadget"] = feature(self.options.with_libudev and self.options.with_v4l)
        tc.project_options["uvch264"] = feature(self.options.with_libudev and self.options.with_libusb)
        tc.project_options["v4l2codecs"] = feature(self.options.with_libudev and self.options.with_v4l)
        tc.project_options["va"] = feature(self.options.with_libva)
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

        tc.project_options["gpl"] = "enabled"  # only applies to libx265 currently
        tc.project_options["doc"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["nls"] = "disabled"
        tc.project_options["orc"] = "disabled"
        tc.project_options["introspection"] = "disabled"  # TODO

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
        # The generated config headers (such as gst/gl/gstglconfig.h) are not installed for some reason
        copy(self, "*config.h",
             os.path.join(self.build_folder, "gst-libs"),
             os.path.join(self.package_folder, "include", "gstreamer-1.0"))
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

        def _define_library(name, extra_requires, interface=False):
            component_name = f"gstreamer-{name}-1.0"
            component = self.cpp_info.components[component_name]
            component.set_property("pkg_config_name", component_name)
            component.requires = [
                "gstreamer::gstreamer-1.0",
                "gstreamer::gstreamer-base-1.0",
            ] + extra_requires
            if not interface:
                component.libs = [f"gst{name.replace('-', '')}-1.0"]
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
        _define_library("adaptivedemux", ["gstreamer-uridownloader-1.0"])
        _define_library("analytics", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_library("bad-audio", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_library("basecamerabinsrc", ["gst-plugins-base::gstreamer-app-1.0"])
        _define_library("codecparsers", [])
        _define_library("codecs", [
            "gstreamer-codecparsers-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        if self.settings.os in ["Linux", "Windows"]:
            _define_library("cuda", ["gst-plugins-base::gstreamer-video-1.0", "gst-plugins-base::gstreamer-gl-prototypes-1.0"])
        _define_library("insertbin", [])
        _define_library("isoff", [])
        _define_library("mpegts", [])
        _define_library("mse", ["gst-plugins-base::gstreamer-app-1.0"])
        if self.options.with_opencv:
            _define_library("opencv", [
                "gst-plugins-base::gstreamer-video-1.0",
                "opencv::opencv_core",
            ])
        _define_library("photography", [])
        _define_library("play", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        _define_library("player", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gstreamer-play-1.0",
        ])
        _define_library("sctp", [])
        _define_library("transcoder", ["gst-plugins-base::gstreamer-pbutils-1.0"])
        if self.options.with_libva and (self.options.with_libdrm or self.settings.os != "Linux"):
            libva = _define_library("va", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "libva::libva_",
            ])
            if self.options.with_libdrm:
                libva.requires.extend([
                    "libva::libva-drm",
                    "libdrm::libdrm_libdrm",
                ])
        _define_library("uridownloader", [])
        if self.options.with_vulkan:
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
        if self.options.get_safe("with_wayland"):
            _define_library("wayland", [
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "libdrm::libdrm_libdrm",
                "wayland::wayland-client",
            ])
        _define_library("webrtc", ["gst-plugins-base::gstreamer-sdp-1.0"])
        if self.options.with_nice:
            _define_library("webrtc-nice", [
                "gst-plugins-base::gstreamer-sdp-1.0",
                "gstreamer-webrtc-1.0",
                "libnice::libnice",
            ])

        # Plugins
        _define_plugin("accurip", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("adpcmdec", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("adpcmenc", ["gst-plugins-base::gstreamer-audio-1.0"])
        if self.options.with_ssl:
            _define_plugin("aes", [
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "openssl::openssl",
            ])
        _define_plugin("aiff", [
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        if self.options.with_pango:
            _define_plugin("analyticsoverlay", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-analytics-1.0",
                "pango::pangocairo",
            ])
        if self.options.with_aom:
            _define_plugin("aom", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libaom-av1::libaom-av1",
            ])
        _define_plugin("asfmux", ["gst-plugins-base::gstreamer-rtp-1.0"])
        _define_plugin("audiobuffersplit", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("audiofxbad", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("audiolatency", [])
        _define_plugin("audiomixmatrix", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("audiovisualizers", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-fft-1.0",
        ])
        _define_plugin("autoconvert", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
        ])
        _define_plugin("bayer", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_bz2:
            _define_plugin("bz2", ["bzip2::bzip2"])
        _define_plugin("camerabin", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gstreamer-photography-1.0",
        ])
        if self.options.with_pango:
            _define_plugin("closedcaption", [
                "gst-plugins-base::gstreamer-video-1.0",
                "pango::pangocairo",
            ])
        if self.options.with_json:
            _define_plugin("codec2json", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-codecparsers-1.0",
                "json-glib::json-glib",
            ])
        _define_plugin("codecalpha", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        _define_plugin("codectimestamper", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gstreamer-codecparsers-1.0",
        ])
        _define_plugin("coloreffects", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_lcms:
            _define_plugin("colormanagement", [
                "gst-plugins-base::gstreamer-video-1.0",
                "lcms::lcms",
            ])
        if self.options.with_libcurl:
            gst_curl = _define_plugin("curl", ["libcurl::libcurl"])
            if self.options.with_libssh2:
                gst_curl.requires.append("libssh2::libssh2")
        if self.options.with_libxml2:
            _define_plugin("dash", [
                "gstreamer-adaptivedemux-1.0",
                "gstreamer-isoff-1.0",
                "gstreamer::gstreamer-net-1.0",
                "gst-plugins-base::gstreamer-tag-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "libxml2::libxml2",
            ])
        if self.options.with_libdc1394:
            _define_plugin("dc1394", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libdc1394::libdc1394",
            ])
        if self.options.with_libde265:
            _define_plugin("de265", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libde265::libde265",
            ])
        _define_plugin("debugutilsbad", [
            "gstreamer::gstreamer-net-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
        ])
        _define_plugin("decklink", [
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-video-1.0"
        ], cpp=True)
        if self.options.with_ssl:
            _define_plugin("dtls", ["openssl::openssl"])
        _define_plugin("dvb", ["gstreamer-mpegts-1.0"])
        _define_plugin("dvbsubenc", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("dvbsuboverlay", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("dvdspu", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_faac:
            _define_plugin("faac", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-tag-1.0",
                "faac::faac",
            ])
        _define_plugin("faceoverlay", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("fbdevsink", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_fdk_aac:
            _define_plugin("fdkaac", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "libfdk_aac::libfdk_aac",
            ])
        _define_plugin("festival", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("fieldanalysis", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("freeverb", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("frei0r", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("gaudieffects", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("gdp", [])
        _define_plugin("geometrictransform", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_google_cloud_storage:
            _define_plugin("gs", ["google-cloud-cpp::storage"], cpp=True)
        if self.options.with_gtk and self.options.get_safe("with_wayland") and self.options.with_libdrm:
            _define_plugin("gtkwayland", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gstreamer-wayland-1.0",
                "gtk::gtk+-3.0",
                "libdrm::libdrm_libdrm",
                "wayland::wayland-client",
            ])
        if self.options.with_ssl:
            _define_plugin("hls", [
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-tag-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-adaptivedemux-1.0",
                "openssl::openssl",
            ])
        _define_plugin("id3tag", ["gst-plugins-base::gstreamer-tag-1.0"])
        _define_plugin("insertbin", ["gstreamer-insertbin-1.0"])
        _define_plugin("interlace", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("inter", ["gst-plugins-base::gstreamer-audio-1.0", "gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("ipcpipeline", [])
        _define_plugin("ivfparse", [])
        _define_plugin("ivtc", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("jp2kdecimator", [])
        _define_plugin("jpegformat", [
            "gst-plugins-base::gstreamer-video-1.0",
            "gst-plugins-base::gstreamer-tag-1.0",
            "gstreamer-codecparsers-1.0",
        ])
        if self.options.with_libdrm:
            _define_plugin("kms", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "libdrm::libdrm_libdrm",
            ])
        _define_plugin("legacyrawparse", ["gst-plugins-base::gstreamer-audio-1.0", "gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("midi", ["gst-plugins-base::gstreamer-tag-1.0"])
        if self.options.with_modplug:
            _define_plugin("modplug", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "libmodplug::libmodplug",
            ], cpp=True)
        _define_plugin("mpegpsdemux", [
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
        ])
        _define_plugin("mpegpsmux", ["gst-plugins-base::gstreamer-pbutils-1.0"])
        _define_plugin("mpegtsdemux", [
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gstreamer-codecparsers-1.0",
            "gstreamer-mpegts-1.0",
        ])
        _define_plugin("mpegtsmux", [
            "gst-plugins-base::gstreamer-tag-1.0",
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-audio-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gstreamer-mpegts-1.0",
        ])
        _define_plugin("mse", ["gstreamer-mse-1.0"])
        _define_plugin("mxf", ["gst-plugins-base::gstreamer-audio-1.0", "gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("netsim", [])
        if self.options.with_onnx:
            gst_onnx = _define_plugin("onnx", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-analytics-1.0",
                "onnxruntime::onnxruntime",
            ])
            if self.settings.os in ["Linux", "Windows"]:
                gst_onnx.requires.append("gstremaer-cuda-1.0")
        if self.options.with_openal:
            _define_plugin("openal", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "openal-soft::openal-soft",
            ])
        if self.options.with_opencv:
            _define_plugin("opencv", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-opencv-1.0",
                "opencv::opencv_bgsegm",
                "opencv::opencv_calib3d",
                "opencv::opencv_core",
                "opencv::opencv_features2d",
                "opencv::opencv_imgcodecs",
                "opencv::opencv_imgproc",
                "opencv::opencv_objdetect",
                "opencv::opencv_tracking",
                "opencv::opencv_video",
            ], cpp=True)
        if self.options.with_openexr:
            _define_plugin("openexr", [
                "gst-plugins-base::gstreamer-video-1.0",
                "openexr::openexr",
            ], cpp=True)
        if self.options.with_openh264:
            _define_plugin("openh264", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "openh264::openh264",
            ], cpp=True)
        if self.options.with_openjpeg:
            _define_plugin("openjpeg", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-codecparsers-1.0",
                "openjpeg::openjpeg",
            ])
        if self.options.with_openni2:
            _define_plugin("openni2", [
                "gst-plugins-base::gstreamer-video-1.0",
                "openni2::openni2",
            ], cpp=True)
        if self.options.with_opus:
            _define_plugin("opusparse", [
                "gst-plugins-base::gstreamer-rtp-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-audio-1.0",
                "gst-plugins-base::gstreamer-tag-1.0",
                "opus::opus",
            ])
        _define_plugin("pcapparse", [])
        _define_plugin("pnm", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("proxy", [])
        if self.options.with_libqrencode and self.options.with_json:
            _define_plugin("qroverlay", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libqrencode::libqrencode",
                "json-glib::json-glib",
            ])
        if self.options.with_libva and (self.options.with_libdrm or self.settings.os != "Linux"):
            _define_plugin("qsv", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gstreamer-codecparsers-1.0",
                "gstreamer-va-1.0",
            ], cpp=True)
        _define_plugin("removesilence", ["gst-plugins-base::gstreamer-audio-1.0"])
        if self.options.get_safe("with_xorg"):
            _define_plugin("rfbsrc", [
                "gst-plugins-base::gstreamer-video-1.0",
                "xorg::x11",
            ])
        _define_plugin("rist", [
            "gst-plugins-base::gstreamer-rtp-1.0",
            "gstreamer::gstreamer-net-1.0",
        ])
        if self.options.with_rsvg:
            _define_plugin("rsvg", [
                "gst-plugins-base::gstreamer-video-1.0",
                "librsvg::librsvg",
            ])
        _define_plugin("rtmp2", [])
        _define_plugin("rtpmanagerbad", [
            "gstreamer::gstreamer-net-1.0",
            "gst-plugins-base::gstreamer-rtp-1.0",
        ])
        _define_plugin("rtponvif", ["gst-plugins-base::gstreamer-rtp-1.0"])
        if self.options.with_sctp:
            _define_plugin("sctp", [
                "gstreamer-sctp-1.0",
                "usrsctp::usrsctp",
            ])
        _define_plugin("sdpelem", [
            "gst-plugins-base::gstreamer-app-1.0",
            "gst-plugins-base::gstreamer-sdp-1.0",
        ])
        _define_plugin("segmentclip", ["gst-plugins-base::gstreamer-audio-1.0", "gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("shm", [])
        _define_plugin("siren", ["gst-plugins-base::gstreamer-audio-1.0"])
        _define_plugin("smooth", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_libxml2:
            _define_plugin("smoothstreaming", [
                "gstreamer-adaptivedemux-1.0",
                "gstreamer-codecparsers-1.0",
                "gstreamer-isoff-1.0",
                "libxml2::libxml2",
            ])
        if self.options.with_sndfile:
            _define_plugin("sndfile", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "libsndfile::libsndfile",
            ])
        if self.options.with_soundtouch:
            _define_plugin("soundtouch", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "soundtouch::soundtouch",
            ], cpp=True)
        _define_plugin("speed", ["gst-plugins-base::gstreamer-audio-1.0"])
        if self.options.with_srt:
            _define_plugin("srt", ["srt::srt"])
        if self.options.with_srtp:
            _define_plugin("srtp", [
                "gst-plugins-base::gstreamer-rtp-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "libsrtp::libsrtp",
            ])
        _define_plugin("subenc", [])
        if self.options.with_svtav1:
            _define_plugin("svtav1", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libsvtav1::encoder",
            ])
        _define_plugin("switchbin", [])
        _define_plugin("timecode", ["gst-plugins-base::gstreamer-audio-1.0", "gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_tinyalsa:
            _define_plugin("tinyalsa", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "tinyalsa::tinyalsa",
            ])
        _define_plugin("transcode", ["gst-plugins-base::gstreamer-pbutils-1.0"])
        if self.options.with_pango and self.options.with_libxml2:
            _define_plugin("ttmlsubs", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libxml2::libxml2",
                "pango::pangocairo",
            ])
        if self.settings.os != "Windows":
            _define_plugin("unixfd", ["gst-plugins-base::gstreamer-allocators-1.0"])
        if self.options.with_libudev and self.options.with_v4l:
            _define_plugin("uvcgadget", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "libgudev::libgudev",
                "libv4l::libv4l2",
            ])
            _define_plugin("v4l2codecs", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gstreamer-codecparsers-1.0",
                "gstreamer-codecs-1.0",
                "libgudev::libgudev",
                "libv4l::libv4l2",
            ])
        if self.options.with_libudev and self.options.with_libusb:
            _define_plugin("uvch264", [
                "gst-plugins-base::gstreamer-app-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "libgudev::libgudev",
                "libusb::libusb",
            ])
        if self.options.with_libva and (self.options.with_libdrm or self.settings.os != "Linux"):
            gst_va = _define_plugin("va", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gstreamer-codecparsers-1.0",
                "gstreamer-codecs-1.0",
                "gstreamer-va-1.0",
            ])
            if self.options.with_libudev:
                gst_va.requires.append("libgudev::libgudev")
        _define_plugin("videofiltersbad", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("videoframe_audiolevel", ["gst-plugins-base::gstreamer-audio-1.0", "gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("videoparsersbad", [
            "gst-plugins-base::gstreamer-pbutils-1.0",
            "gst-plugins-base::gstreamer-video-1.0",
            "gstreamer-codecparsers-1.0",
        ])
        _define_plugin("videosignal", ["gst-plugins-base::gstreamer-video-1.0"])
        _define_plugin("vmnc", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_voamrwbenc:
            _define_plugin("voamrwbenc", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-tag-1.0",
                "vo-amrwbenc::vo-amrwbenc",
            ])
        if self.options.with_vulkan:
            _define_plugin("vulkan", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gstreamer-vulkan-1.0",
                "gstreamer-codecparsers-1.0",
                "gstreamer-codecs-1.0",
                "vulkan-loader::vulkan-loader",
            ])
        if self.options.with_wayland and self.options.with_libdrm:
            _define_plugin("waylandsink", [
                "gst-plugins-base::gstreamer-video-1.0",
                "gst-plugins-base::gstreamer-allocators-1.0",
                "gstreamer-wayland-1.0",
                "libdrm::libdrm_libdrm",
                "wayland::wayland-client",
            ])
        if self.options.with_webp:
            _define_plugin("webp", [
                "gst-plugins-base::gstreamer-video-1.0",
                "libwebp::libwebp",
            ])
        gst_webrtc = _define_plugin("webrtc", [
            "gst-plugins-base::gstreamer-app-1.0",
            "gst-plugins-base::gstreamer-rtp-1.0",
            "gst-plugins-base::gstreamer-sdp-1.0",
            "gstreamer-webrtc-1.0",
            "gstreamer-sctp-1.0",
        ])
        if self.options.with_nice:
            gst_webrtc.requires.append("gstreamer-webrtc-nice-1.0")
        if self.options.with_wildmidi:
            _define_plugin("wildmidi", [
                "gst-plugins-base::gstreamer-audio-1.0",
                "gstreamer-bad-audio-1.0",
                "wildmidi::wildmidi",
            ])
        if self.options.with_x265:
            _define_plugin("x265", [
                "gst-plugins-base::gstreamer-pbutils-1.0",
                "gst-plugins-base::gstreamer-video-1.0",
                "libx265::libx265",
            ])
        _define_plugin("y4mdec", ["gst-plugins-base::gstreamer-video-1.0"])
        if self.options.with_zbar:
            _define_plugin("zbar", [
                "gst-plugins-base::gstreamer-video-1.0",
                "zbar::zbar",
            ])
        if self.options.with_zxing:
            _define_plugin("zxing", [
                "gst-plugins-base::gstreamer-video-1.0",
                "zxing-cpp::zxing-cpp",
            ], cpp=True)

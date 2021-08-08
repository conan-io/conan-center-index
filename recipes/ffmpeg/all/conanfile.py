from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob
import shutil

required_conan_version = ">=1.33.0"


class FFMpegConan(ConanFile):
    name = "ffmpeg"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    # https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md
    license = ("LGPL-2.1-or-later", "GPL-2.0-or-later")
    homepage = "https://ffmpeg.org"
    topics = ("ffmpeg", "multimedia", "audio", "video", "encoder", "decoder", "encoding", "decoding",
             "transcoding", "multiplexer", "demultiplexer", "streaming")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_postproc": [True, False],
        "with_zlib": [True, False],
        "with_bzlib": [True, False],
        "with_lzma": [True, False],
        "with_iconv": [True, False],
        "with_freetype": [True, False],
        "with_openjpeg": [True, False],
        "with_openh264": [True, False],
        "with_opus": [True, False],
        "with_vorbis": [True, False],
        "with_zmq": [True, False],
        "with_sdl2": [True, False],
        "with_x264": [True, False],
        "with_x265": [True, False],
        "with_vpx": [True, False],
        "with_mp3lame": [True, False],
        "with_fdk_aac": [True, False],
        "with_webp": [True, False],
        "with_ssl": [False, "openssl", "securetransport"],
        "with_alsa": [True, False],
        "with_pulse": [True, False],
        "with_vaapi": [True, False],
        "with_vdpau": [True, False],
        "with_xcb": [True, False],
        "with_appkit": [True, False],
        "with_avfoundation": [True, False],
        "with_coreimage": [True, False],
        "with_audiotoolbox": [True, False],
        "with_videotoolbox": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_postproc": True,
        "with_zlib": True,
        "with_bzlib": True,
        "with_lzma": True,
        "with_iconv": True,
        "with_freetype": True,
        "with_openjpeg": True,
        "with_openh264": True,
        "with_opus": True,
        "with_vorbis": True,
        "with_zmq": False,
        "with_sdl2": False,
        "with_x264": True,
        "with_x265": True,
        "with_vpx": True,
        "with_mp3lame": True,
        "with_fdk_aac": True,
        "with_webp": True,
        "with_ssl": "openssl",
        "with_alsa": True,
        "with_pulse": True,
        "with_vaapi": True,
        "with_vdpau": True,
        "with_xcb": True,
        "with_appkit": True,
        "with_avfoundation": True,
        "with_coreimage": True,
        "with_audiotoolbox": True,
        "with_videotoolbox": True,
    }

    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self.settings.os in ["Linux", "FreeBSD"]:
            del self.options.with_vaapi
            del self.options.with_vdpau
            del self.options.with_xcb
            del self.options.with_alsa
            del self.options.with_pulse
        if self.settings.os != "Macos":
            del self.options.with_appkit
            del self.options.with_avfoundation
            del self.options.with_coreimage
            del self.options.with_audiotoolbox
            del self.options.with_videotoolbox

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")
        self.build_requires("pkgconf/1.7.4")
        if self.settings.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_iconv:
            self.requires("libiconv/1.16")
        if self.options.with_freetype:
            self.requires("freetype/2.10.4")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.4.0")
        if self.options.with_openh264:
            self.requires("openh264/1.7.0")
        if self.options.with_vorbis:
            self.requires("vorbis/1.3.7")
        if self.options.with_opus:
            self.requires("opus/1.3.1")
        if self.options.with_zmq:
            self.requires("zeromq/4.3.4")
        if self.options.with_sdl2:
            self.requires("sdl/2.0.14")
        if self.options.with_x264:
            self.requires("libx264/20190605")
        if self.options.with_x265:
            self.requires("libx265/3.4")
        if self.options.with_vpx:
            self.requires("libvpx/1.9.0")
        if self.options.with_mp3lame:
            self.requires("libmp3lame/3.100")
        if self.options.with_fdk_aac:
            self.requires("libfdk_aac/2.0.2")
        if self.options.with_webp:
            self.requires("libwebp/1.0.3")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1k")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_alsa:
                self.requires("libalsa/1.1.9")
            if self.options.with_xcb:
                self.requires("xorg/system")
            if self.options.with_pulse:
                self.requires("pulseaudio/13.0")
            if self.options.with_vaapi:
                self.requires("vaapi/system")
            if self.options.with_vdpau:
                self.requires("vdpau/system")

    def validate(self):
        if self.settings.os != "Macos" and self.options.with_ssl == "securetransport":
            raise ConanInvalidConfiguration("securetransport is only available on Macos")
        if self.settings.os == "Macos" and self.settings.arch == "armv8" and self.options.with_vpx:
            raise ConanInvalidConfiguration("libvpx doesn't support armv8 supported yet")
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.with_sdl2:
            raise ConanInvalidConfiguration("sdl2 not supported yet")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio" and self.options.with_x264 and not self.options["libx264"].shared:
            # suppress MSVC linker warnings: https://trac.ffmpeg.org/ticket/7396
            # warning LNK4049: locally defined symbol x264_levels imported
            # warning LNK4049: locally defined symbol x264_bit_depth imported
            tools.replace_in_file(os.path.join(self._source_subfolder, "libavcodec", "libx264.c"),
                                  "#define X264_API_IMPORTS 1", "")
        if self.options.with_ssl == "openssl":
            # https://trac.ffmpeg.org/ticket/5675
            openssl_libraries = " ".join(["-l%s" % lib for lib in self.deps_cpp_info["openssl"].libs])
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "check_lib openssl openssl/ssl.h SSL_library_init -lssl -lcrypto -lws2_32 -lgdi32 ||",
                                  "check_lib openssl openssl/ssl.h OPENSSL_init_ssl %s || " % openssl_libraries)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = ["--disable-doc",
                "--disable-programs"]
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        args.append("--pkg-config-flags=--static")
        if self.settings.build_type == "Debug":
            args.extend(["--disable-optimizations", "--disable-mmx", "--disable-stripping", "--enable-debug"])
        # since ffmpeg"s build system ignores CC and CXX
        if tools.get_env("CC"):
            args.append("--cc=%s" % tools.get_env("CC"))
        if tools.get_env("CC"):
            args.append("--cxx=%s" % tools.get_env("CXX"))
        if self.settings.compiler == "Visual Studio":
            args.append("--toolchain=msvc")
            args.append("--extra-cflags=-%s" % self.settings.compiler.runtime)
            if int(str(self.settings.compiler.version)) <= 12:
                # Visual Studio 2013 (and earlier) doesn"t support "inline" keyword for C (only for C++)
                args.append("--extra-cflags=-Dinline=__inline" % self.settings.compiler.runtime)

        if self.settings.arch == "x86":
            args.append("--arch=x86")

        if self.options.get_safe("fPIC", True):
            args.append("--enable-pic")

        if not self.options.with_postproc:
            args.append("--disable-postproc")
        if not self.options.with_bzlib:
            args.append("--disable-zlib")
        if not self.options.with_zlib:
            args.append("--disable-zlib")
        if not self.options.with_lzma:
            args.append("--disable-lzma")
        if not self.options.with_iconv:
            args.append("--disable-iconv")
        if self.options.with_freetype:
            args.append("--enable-libfreetype")
        if self.options.with_openjpeg:
            args.append("--enable-libopenjpeg")
        if self.options.with_openh264:
            args.append("--enable-libopenh264")
        if self.options.with_vorbis:
            args.append("--enable-libvorbis")
        if self.options.with_opus:
            args.append("--enable-libopus")
        if self.options.with_zmq:
            args.append("--enable-libzmq")
        if not self.options.with_sdl2:
            args.append("--disable-sdl2")
        if self.options.with_x264:
            args.append("--enable-libx264")
        if self.options.with_x265:
            args.append("--enable-libx265")
        if self.options.with_vpx:
            args.append("--enable-libvpx")
        if self.options.with_mp3lame:
            args.append("--enable-libmp3lame")
        if self.options.with_fdk_aac:
            args.append("--enable-libfdk-aac")
        if self.options.with_webp:
            args.append("--enable-libwebp")
        if self.options.with_ssl == "openssl":
            args.append("--enable-openssl")

        if self.options.with_x264 or self.options.with_x265 or self.options.with_postproc:
            args.append("--enable-gpl")

        if self.options.with_fdk_aac:
            args.append("--enable-nonfree")

        if self.settings.os in ["Linux", "FreeBSD"]:
            if not self.options.with_alsa:
                args.append("--disable-alsa")
            if self.options.with_pulse:
                args.append("--enable-libpulse")
            if not self.options.with_vaapi:
                args.append("--disable-vaapi")
            if not self.options.with_vdpau:
                args.append("--disable-vdpau")
            if self.options.with_xcb:
                args.extend(["--enable-libxcb", "--enable-libxcb-shm",
                             "--enable-libxcb-shape", "--enable-libxcb-xfixes"])

        if self.settings.os == "Macos":
            if not self.options.with_appkit:
                args.append("--disable-appkit")
            if not self.options.with_avfoundation:
                args.append("--disable-avfoundation")
            if not self.options.with_coreimage:
                args.append("--disable-coreimage")
            if not self.options.with_audiotoolbox:
                args.append("--disable-audiotoolbox")
            if not self.options.with_videotoolbox:
                args.append("--disable-videotoolbox")
            if self.options.with_ssl != "securetransport":
                args.append("--disable-securetransport")

        # FIXME disable CUDA and CUVID by default, revisit later
        args.extend(["--disable-cuda", "--disable-cuvid"])

        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            # ffmpeg produces .a files which are actually .lib files
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                libs = glob.glob("*.a")
                for lib in libs:
                    shutil.move(lib, lib[:-2] + ".lib")

    def package_info(self):
        libs = ["avdevice", "avfilter", "avformat", "avcodec", "swresample", "swscale", "avutil"]
        if self.options.with_postproc:
            libs.insert(-1, 'postproc')
        for lib in libs:
            self.cpp_info.components[lib].libs = [lib]
            self.cpp_info.components[lib].names["pkg_config"] = lib

        if self.options.with_zlib:
            self.cpp_info.components["avformat"].requires.append("zlib::zlib")
            self.cpp_info.components["avcodec"].requires.append("zlib::zlib")
        if self.options.with_bzlib:
            self.cpp_info.components["avformat"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["avcodec"].requires.append("xz_utils::xz_utils")
        if self.options.with_iconv:
            self.cpp_info.components["avformat"].requires.append("libiconv::libiconv")
            self.cpp_info.components["avcodec"].requires.append("libiconv::libiconv")
        if self.options.with_freetype:
            self.cpp_info.components["avfilter"].requires.append("freetype::freetype")
        if self.options.with_openjpeg:
            self.cpp_info.components["avcodec"].requires.append("openjpeg::openjpeg")
        if self.options.with_openh264:
            self.cpp_info.components["avcodec"].requires.append("openh264::openh264")
        if self.options.with_vorbis:
            self.cpp_info.components["avcodec"].requires.append("vorbis::vorbis")
        if self.options.with_opus:
            self.cpp_info.components["avcodec"].requires.append("opus::opus")
        if self.options.with_x264:
            self.cpp_info.components["avcodec"].requires.append("libx264::libx264")
        if self.options.with_x265:
            self.cpp_info.components["avcodec"].requires.append("libx265::libx265")
        if self.options.with_vpx:
            self.cpp_info.components["avcodec"].requires.append("libvpx::libvpx")
        if self.options.with_mp3lame:
            self.cpp_info.components["avcodec"].requires.append("libmp3lame::libmp3lame")
        if self.options.with_fdk_aac:
            self.cpp_info.components["avcodec"].requires.append("libfdk_aac::libfdk_aac")
        if self.options.with_webp:
            self.cpp_info.components["avcodec"].requires.append("libwebp::libwebp")
        if self.options.with_ssl == "openssl":
            self.cpp_info.components["avformat"].requires.append("openssl::ssl")

        if self.settings.os == "Macos":
            self.cpp_info.components["avdevice"].frameworks = ["CoreFoundation", "Foundation", "CoreGraphics", "OpenGL"]
            self.cpp_info.components["avfilter"].frameworks = ["OpenGL", "CoreGraphics"]
            self.cpp_info.components["avcodec"].frameworks = ["CoreVideo", "CoreMedia"]
            if self.options.with_appkit:
                self.cpp_info.components["avdevice"].frameworks.append("AppKit")
                self.cpp_info.components["avfilter"].frameworks.append("AppKit")
            if self.options.with_avfoundation:
                self.cpp_info.components["avdevice"].frameworks.append("AVFoundation")
            if self.options.with_coreimage:
                self.cpp_info.components["avfilter"].frameworks = ["CoreImage"]
            if self.options.with_audiotoolbox:
                self.cpp_info.components["avcodec"].frameworks.append("AudioToolbox")
            if self.options.with_videotoolbox:
                self.cpp_info.components["avcodec"].frameworks.append("VideoToolbox")
            if self.options.with_ssl == "securetransport":
                self.cpp_info.components["avformat"].frameworks.append("Security")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_alsa:
                self.cpp_info.components["avdevice"].requires.append("libalsa::libalsa")
            if self.options.with_xcb:
                self.cpp_info.components["avdevice"].requires.append("xorg::xcb")
            if self.options.with_pulse:
                self.cpp_info.components["avdevice"].requires.append("pulseaudio::pulseaudio")
            if self.options.with_vaapi:
                self.cpp_info.components["avcodec"].requires.append("vaapi::vaapi")
            if self.options.with_vdpau:
                self.cpp_info.components["avcodec"].requires.append("vdpau::vdpau")
            if self.options.fPIC:
                # https://trac.ffmpeg.org/ticket/1713
                # https://ffmpeg.org/platform.html#Advanced-linking-configuration
                # https://ffmpeg.org/pipermail/libav-user/2014-December/007719.html
                self.cpp_info.components["avcodec"].sharedlinkflags.append("-Wl,-Bsymbolic")
        elif self.settings.os == "Windows":
            self.cpp_info.components["avdevice"].system_libs.extend(["ws2_32", "secur32", "shlwapi", "strmiids", "vfw32", "bcrypt"])

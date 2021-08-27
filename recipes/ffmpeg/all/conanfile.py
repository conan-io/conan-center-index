from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import glob
import shutil


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
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "postproc": [True, False],
               "zlib": [True, False],
               "bzlib": [True, False],
               "lzma": [True, False],
               "iconv": [True, False],
               "freetype": [True, False],
               "openjpeg": [True, False],
               "openh264": [True, False],
               "opus": [True, False],
               "vorbis": [True, False],
               "zmq": [True, False],
               "sdl2": [True, False],
               "x264": [True, False],
               "x265": [True, False],
               "vpx": [True, False],
               "mp3lame": [True, False],
               "fdk_aac": [True, False],
               "webp": [True, False],
               "openssl": [True, False],
               "alsa": [True, False],
               "pulse": [True, False],
               "vaapi": [True, False],
               "vdpau": [True, False],
               "xcb": [True, False],
               "appkit": [True, False],
               "avfoundation": [True, False],
               "coreimage": [True, False],
               "audiotoolbox": [True, False],
               "videotoolbox": [True, False],
               "securetransport": [True, False],
               "qsv": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "postproc": True,
                       "zlib": True,
                       "bzlib": True,
                       "lzma": True,
                       "iconv": True,
                       "freetype": True,
                       "openjpeg": True,
                       "openh264": True,
                       "opus": True,
                       "vorbis": True,
                       "zmq": False,
                       "sdl2": False,
                       "x264": True,
                       "x265": True,
                       "vpx": True,
                       "mp3lame": True,
                       "fdk_aac": True,
                       "webp": True,
                       "openssl": True,
                       "alsa": True,
                       "pulse": True,
                       "vaapi": True,
                       "vdpau": True,
                       "xcb": True,
                       "appkit": True,
                       "avfoundation": True,
                       "coreimage": True,
                       "audiotoolbox": True,
                       "videotoolbox": True,
                       "securetransport": False,  # conflicts with OpenSSL
                       "qsv": False}
    generators = "pkg_config"
    _source_subfolder = "source_subfolder"

    _autotools = None

    @property
    def _is_mingw_windows(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc" and os.name == "nt"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination = self._source_subfolder, strip_root=True)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.vaapi
            del self.options.vdpau
            del self.options.xcb
            del self.options.alsa
            del self.options.pulse
        if self.settings.os != "Macos":
            del self.options.appkit
            del self.options.avfoundation
            del self.options.coreimage
            del self.options.audiotoolbox
            del self.options.videotoolbox
            del self.options.securetransport
        if self.settings.os != "Windows":
            del self.options.qsv

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ:
                self.build_requires("msys2/20200517")
        if self.settings.os == "Linux":
            if not tools.which("pkg-config"):
                self.build_requires("pkgconf/1.7.3")

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.iconv:
            self.requires("libiconv/1.16")
        if self.options.freetype:
            self.requires("freetype/2.10.4")
        if self.options.openjpeg:
            self.requires("openjpeg/2.4.0")
        if self.options.openh264:
            self.requires("openh264/1.7.0")
        if self.options.vorbis:
            self.requires("vorbis/1.3.7")
        if self.options.opus:
            self.requires("opus/1.3.1")
        if self.options.zmq:
            self.requires("zeromq/4.3.3")
        if self.options.sdl2:
            self.requires("sdl/2.0.16")
        if self.options.x264:
            self.requires("libx264/20190605")
        if self.options.x265:
            self.requires("libx265/3.4")
        if self.options.vpx:
            self.requires("libvpx/1.9.0")
        if self.options.mp3lame:
            self.requires("libmp3lame/3.100")
        if self.options.fdk_aac:
            self.requires("libfdk_aac/2.0.0")
        if self.options.webp:
            self.requires("libwebp/1.0.3")
        if self.options.openssl:
            self.requires("openssl/1.1.1h")
        if self.settings.os == "Windows":
            if self.options.qsv:
                raise ConanInvalidConfiguration("intel_media_sdk package does not exist (yet)")
                self.requires("intel_media_sdk/2018R2_1")
        if self.settings.os == "Linux":
            if self.options.alsa:
                self.requires("libalsa/1.1.9")
            if self.options.xcb:
                self.requires("xorg/system")
            if self.options.pulse:
                self.requires("pulseaudio/13.0")
            if self.options.vaapi:
                self.requires("vaapi/system")
            if self.options.vdpau:
                self.requires("vdpau/system")


    def _patch_sources(self):
        if self._is_msvc and self.options.x264 and not self.options["libx264"].shared:
            # suppress MSVC linker warnings: https://trac.ffmpeg.org/ticket/7396
            # warning LNK4049: locally defined symbol x264_levels imported
            # warning LNK4049: locally defined symbol x264_bit_depth imported
            tools.replace_in_file(os.path.join(self._source_subfolder, "libavcodec", "libx264.c"),
                                  "#define X264_API_IMPORTS 1", "")
        if self.options.openssl:
            # https://trac.ffmpeg.org/ticket/5675
            openssl_libraries = " ".join(["-l%s" % lib for lib in self.deps_cpp_info["openssl"].libs])
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "check_lib openssl openssl/ssl.h SSL_library_init -lssl -lcrypto -lws2_32 -lgdi32 ||",
                                  "check_lib openssl openssl/ssl.h OPENSSL_init_ssl %s || " % openssl_libraries)

    def _get_autotools(self):
        if self._autotools:
            return self._autotools

        prefix = tools.unix_path(self.package_folder) if self.settings.os == "Windows" else self.package_folder
        args = ["--prefix=%s" % prefix,
                "--disable-doc",
                "--disable-programs"]
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        args.append("--pkg-config-flags=--static")
        if self.settings.build_type == "Debug":
            args.extend(["--disable-optimizations", "--disable-mmx", "--disable-stripping", "--enable-debug"])
        # since ffmpeg"s build system ignores CC and CXX
        if "CC" in os.environ:
            args.append("--cc=%s" % os.environ["CC"])
        if "CXX" in os.environ:
            args.append("--cxx=%s" % os.environ["CXX"])
        if self._is_msvc:
            args.append("--toolchain=msvc")
            args.append("--extra-cflags=-%s" % self.settings.compiler.runtime)
            if int(str(self.settings.compiler.version)) <= 12:
                # Visual Studio 2013 (and earlier) doesn"t support "inline" keyword for C (only for C++)
                args.append("--extra-cflags=-Dinline=__inline" % self.settings.compiler.runtime)

        if self.settings.arch == "x86":
            args.append("--arch=x86")

        if self.settings.os != "Windows":
            args.append("--enable-pic" if self.options.fPIC else "--disable-pic")

        args.append("--enable-postproc" if self.options.postproc else "--disable-postproc")
        args.append("--enable-zlib" if self.options.zlib else "--disable-zlib")
        args.append("--enable-bzlib" if self.options.bzlib else "--disable-bzlib")
        args.append("--enable-lzma" if self.options.lzma else "--disable-lzma")
        args.append("--enable-iconv" if self.options.iconv else "--disable-iconv")
        args.append("--enable-libfreetype" if self.options.freetype else "--disable-libfreetype")
        args.append("--enable-libopenjpeg" if self.options.openjpeg else "--disable-libopenjpeg")
        args.append("--enable-libopenh264" if self.options.openh264 else "--disable-libopenh264")
        args.append("--enable-libvorbis" if self.options.vorbis else "--disable-libvorbis")
        args.append("--enable-libopus" if self.options.opus else "--disable-libopus")
        args.append("--enable-libzmq" if self.options.zmq else "--disable-libzmq")
        args.append("--enable-sdl2" if self.options.sdl2 else "--disable-sdl2")
        args.append("--enable-libx264" if self.options.x264 else "--disable-libx264")
        args.append("--enable-libx265" if self.options.x265 else "--disable-libx265")
        args.append("--enable-libvpx" if self.options.vpx else "--disable-libvpx")
        args.append("--enable-libmp3lame" if self.options.mp3lame else "--disable-libmp3lame")
        args.append("--enable-libfdk-aac" if self.options.fdk_aac else "--disable-libfdk-aac")
        args.append("--enable-libwebp" if self.options.webp else "--disable-libwebp")
        args.append("--enable-openssl" if self.options.openssl else "--disable-openssl")

        if self.options.x264 or self.options.x265 or self.options.postproc:
            args.append("--enable-gpl")

        if self.options.fdk_aac:
            args.append("--enable-nonfree")

        if self.settings.os == "Linux":
            args.append("--enable-alsa" if self.options.alsa else "--disable-alsa")
            args.append("--enable-libpulse" if self.options.pulse else "--disable-libpulse")
            args.append("--enable-vaapi" if self.options.vaapi else "--disable-vaapi")
            args.append("--enable-vdpau" if self.options.vdpau else "--disable-vdpau")
            if self.options.xcb:
                args.extend(["--enable-libxcb", "--enable-libxcb-shm",
                                "--enable-libxcb-shape", "--enable-libxcb-xfixes"])
            else:
                args.extend(["--disable-libxcb", "--disable-libxcb-shm",
                                "--disable-libxcb-shape", "--disable-libxcb-xfixes"])

        if self.settings.os == "Macos":
            args.append("--enable-appkit" if self.options.appkit else "--disable-appkit")
            args.append("--enable-avfoundation" if self.options.avfoundation else "--disable-avfoundation")
            args.append("--enable-coreimage" if self.options.avfoundation else "--disable-coreimage")
            args.append("--enable-audiotoolbox" if self.options.audiotoolbox else "--disable-audiotoolbox")
            args.append("--enable-videotoolbox" if self.options.videotoolbox else "--disable-videotoolbox")
            args.append("--enable-securetransport" if self.options.securetransport else "--disable-securetransport")

        if self.settings.os == "Windows":
            args.append("--enable-libmfx" if self.options.qsv else "--disable-libmfx")

        # FIXME disable CUDA and CUVID by default, revisit later
        args.extend(["--disable-cuda", "--disable-cuvid"])

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._is_mingw_windows or self._is_msvc)
        # ffmpeg"s configure is not actually from autotools, so it doesn"t understand standard options like
        # --host, --build, --target
        self._autotools.configure(args=args, build=False, host=False, target=False)
        return self._autotools

    def build(self):
        self._patch_sources()
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.chdir(self._source_subfolder):
                autotools = self._get_autotools()
                autotools.make()

    def package(self):
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.chdir(self._source_subfolder):
                autotools = self._get_autotools()
                autotools.make(args=["install"])
        self.copy(src=self._source_subfolder, pattern="COPYING*", dst=os.path.join(self.package_folder, "licenses"))
        if self._is_msvc and not self.options.shared:
            # ffmpeg produces .a files which are actually .lib files
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                libs = glob.glob("*.a")
                for lib in libs:
                    shutil.move(lib, lib[:-2] + ".lib")

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share")) # this only contains examples

    def package_info(self):
        libs = ["avdevice", "avfilter", "avformat", "avcodec", "swresample", "swscale", "avutil"]

        if self.options.postproc:
            libs.insert(-1, 'postproc')
        if self._is_msvc:
            if self.options.shared:
                self.cpp_info.libs = libs
                self.cpp_info.libdirs.append("bin")
            else:
                self.cpp_info.libs = ["lib" + lib for lib in libs]
        else:
            self.cpp_info.libs = libs
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreVideo", "CoreMedia", "CoreGraphics", "CoreFoundation", "OpenGL", "Foundation"]
            if self.options.appkit:
                self.cpp_info.frameworks.append("AppKit")
            if self.options.avfoundation:
                self.cpp_info.frameworks.append("AVFoundation")
            if self.options.coreimage:
                self.cpp_info.frameworks.append("CoreImage")
            if self.options.audiotoolbox:
                self.cpp_info.frameworks.append("AudioToolbox")
            if self.options.videotoolbox:
                self.cpp_info.frameworks.append("VideoToolbox")
            if self.options.securetransport:
                self.cpp_info.frameworks.append("Security")
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
            if self.settings.os != "Windows" and self.options.fPIC:
                # https://trac.ffmpeg.org/ticket/1713
                # https://ffmpeg.org/platform.html#Advanced-linking-configuration
                # https://ffmpeg.org/pipermail/libav-user/2014-December/007719.html
                self.cpp_info.sharedlinkflags.append("-Wl,-Bsymbolic")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "secur32", "shlwapi", "strmiids", "vfw32", "bcrypt"])

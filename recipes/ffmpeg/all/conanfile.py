from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import contextlib
import glob
import shutil
import re

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
        "postproc": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "with_lzma": [True, False],
        "with_libiconv": [True, False],
        "with_freetype": [True, False],
        "with_openjpeg": [True, False],
        "with_openh264": [True, False],
        "with_opus": [True, False],
        "with_vorbis": [True, False],
        "with_zeromq": [True, False],
        "with_sdl": [True, False],
        "with_libx264": [True, False],
        "with_libx265": [True, False],
        "with_libvpx": [True, False],
        "with_libmp3lame": [True, False],
        "with_libfdk_aac": [True, False],
        "with_libwebp": [True, False],
        "with_ssl": [False, "openssl", "securetransport"],
        "with_libalsa": [True, False],
        "with_pulse": [True, False],
        "with_vaapi": [True, False],
        "with_vdpau": [True, False],
        "with_xcb": [True, False],
        "with_appkit": [True, False],
        "with_avfoundation": [True, False],
        "with_coreimage": [True, False],
        "with_audiotoolbox": [True, False],
        "with_videotoolbox": [True, False],
        "with_programs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "postproc": True,
        "with_zlib": True,
        "with_bzip2": True,
        "with_lzma": True,
        "with_libiconv": True,
        "with_freetype": True,
        "with_openjpeg": True,
        "with_openh264": True,
        "with_opus": True,
        "with_vorbis": True,
        "with_zeromq": False,
        "with_sdl": False,
        "with_libx264": True,
        "with_libx265": True,
        "with_libvpx": True,
        "with_libmp3lame": True,
        "with_libfdk_aac": True,
        "with_libwebp": True,
        "with_ssl": "openssl",
        "with_libalsa": True,
        "with_pulse": True,
        "with_vaapi": True,
        "with_vdpau": True,
        "with_xcb": True,
        "with_appkit": True,
        "with_avfoundation": True,
        "with_coreimage": True,
        "with_audiotoolbox": True,
        "with_videotoolbox": True,
        "with_programs": True,
    }

    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self.settings.os in ["Linux", "FreeBSD"]:
            del self.options.with_vaapi
            del self.options.with_vdpau
            del self.options.with_xcb
            del self.options.with_libalsa
            del self.options.with_pulse
        if self.settings.os != "Macos":
            del self.options.with_appkit
        if self.settings.os not in ["Macos", "iOS", "tvOS"]:
            del self.options.with_coreimage
            del self.options.with_audiotoolbox
            del self.options.with_videotoolbox
        if not tools.is_apple_os(self.settings.os):
            del self.options.with_avfoundation

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_libiconv:
            self.requires("libiconv/1.16")
        if self.options.with_freetype:
            self.requires("freetype/2.11.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.4.0")
        if self.options.with_openh264:
            self.requires("openh264/2.1.1")
        if self.options.with_vorbis:
            self.requires("vorbis/1.3.7")
        if self.options.with_opus:
            self.requires("opus/1.3.1")
        if self.options.with_zeromq:
            self.requires("zeromq/4.3.4")
        if self.options.with_sdl:
            self.requires("sdl/2.0.16")
        if self.options.with_libx264:
            self.requires("libx264/20191217")
        if self.options.with_libx265:
            self.requires("libx265/3.4")
        if self.options.with_libvpx:
            self.requires("libvpx/1.10.0")
        if self.options.with_libmp3lame:
            self.requires("libmp3lame/3.100")
        if self.options.with_libfdk_aac:
            self.requires("libfdk_aac/2.0.2")
        if self.options.with_libwebp:
            self.requires("libwebp/1.2.1")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1l")
        if self.options.get_safe("with_libalsa"):
            self.requires("libalsa/1.2.5.1")
        if self.options.get_safe("with_xcb") or self.options.get_safe("with_vaapi"):
            self.requires("xorg/system")
        if self.options.get_safe("with_pulse"):
            self.requires("pulseaudio/14.2")
        if self.options.get_safe("with_vaapi"):
            self.requires("vaapi/system")
        if self.options.get_safe("with_vdpau"):
            self.requires("vdpau/system")

    def validate(self):
        if self.options.with_ssl == "securetransport" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("securetransport is only available on Apple")

    def build_requirements(self):
        if self.settings.arch in ("x86", "x86_64"):
            self.build_requires("yasm/1.3.0")
        self.build_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _target_arch(self):
        target_arch, _, _ = tools.get_gnu_triplet(
            "Macos" if tools.is_apple_os(self.settings.os) else str(self.settings.os),
            str(self.settings.arch),
            str(self.settings.compiler) if self.settings.os == "Windows" else None,
        ).split("-")
        return target_arch

    @property
    def _target_os(self):
        if self.settings.compiler == "Visual Studio":
            return "win32"
        else:
            _, _, target_os = tools.get_gnu_triplet(
                "Macos" if tools.is_apple_os(self.settings.os) else str(self.settings.os),
                str(self.settings.arch),
                str(self.settings.compiler) if self.settings.os == "Windows" else None,
            ).split("-")
            return target_os

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio" and self.options.with_libx264 and not self.options["libx264"].shared:
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

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        opt_enable_disable = lambda what, v: "--{}-{}".format("enable" if v else "disable", what)
        args = [
            "--pkg-config-flags=--static",
            "--disable-doc",
            opt_enable_disable("cross-compile", tools.cross_building(self)),
            # Libraries
            opt_enable_disable("shared", self.options.shared),
            opt_enable_disable("static", not self.options.shared),
            opt_enable_disable("pic", self.options.get_safe("fPIC", True)),
            opt_enable_disable("postproc", self.options.postproc),
            # Dependencies
            opt_enable_disable("bzlib", self.options.with_bzip2),
            opt_enable_disable("zlib", self.options.with_zlib),
            opt_enable_disable("lzma", self.options.with_lzma),
            opt_enable_disable("iconv", self.options.with_libiconv),
            opt_enable_disable("libopenjpeg", self.options.with_openjpeg),
            opt_enable_disable("libopenh264", self.options.with_openh264),
            opt_enable_disable("libvorbis", self.options.with_vorbis),
            opt_enable_disable("libopus", self.options.with_opus),
            opt_enable_disable("libzmq", self.options.with_zeromq),
            opt_enable_disable("sdl2", self.options.with_sdl),
            opt_enable_disable("libx264", self.options.with_libx264),
            opt_enable_disable("libx265", self.options.with_libx265),
            opt_enable_disable("libvpx", self.options.with_libvpx),
            opt_enable_disable("libmp3lame", self.options.with_libmp3lame),
            opt_enable_disable("libfdk-aac", self.options.with_libfdk_aac),
            opt_enable_disable("libwebp", self.options.with_libwebp),
            opt_enable_disable("openssl", self.options.with_ssl == "openssl"),
            opt_enable_disable("alsa", self.options.get_safe("with_libalsa")),
            opt_enable_disable("libpulse", self.options.get_safe("with_pulse")),
            opt_enable_disable("vaapi", self.options.get_safe("with_vaapi")),
            opt_enable_disable("vdpau", self.options.get_safe("with_vdpau")),
            opt_enable_disable("libxcb", self.options.get_safe("with_xcb")),
            opt_enable_disable("libxcb-shm", self.options.get_safe("with_xcb")),
            opt_enable_disable("libxcb-shape", self.options.get_safe("with_xcb")),
            opt_enable_disable("libxcb-xfixes", self.options.get_safe("with_xcb")),
            opt_enable_disable("appkit", self.options.get_safe("with_appkit")),
            opt_enable_disable("avfoundation", self.options.get_safe("with_avfoundation")),
            opt_enable_disable("coreimage", self.options.get_safe("with_coreimage")),
            opt_enable_disable("audiotoolbox", self.options.get_safe("with_audiotoolbox")),
            opt_enable_disable("videotoolbox", self.options.get_safe("with_videotoolbox")),
            opt_enable_disable("securetransport", self.options.with_ssl == "securetransport"),
            "--disable-cuda",  # FIXME: CUDA support
            "--disable-cuvid",  # FIXME: CUVID support
            # Licenses
            opt_enable_disable("nonfree", self.options.with_libfdk_aac),
            opt_enable_disable("gpl", self.options.with_libx264 or self.options.with_libx265 or self.options.postproc)
        ]
        args.append("--arch={}".format(self._target_arch))
        if self.settings.build_type == "Debug":
            args.extend([
                "--disable-optimizations",
                "--disable-mmx",
                "--disable-stripping",
                "--enable-debug",
            ])
        if not self.options.with_programs:
            args.append("--disable-programs")
        # since ffmpeg"s build system ignores CC and CXX
        if tools.get_env("AS"):
            args.append("--as={}".format(tools.get_env("AS")))
        if tools.get_env("CC"):
            args.append("--cc={}".format(tools.get_env("CC")))
        if tools.get_env("CXX"):
            args.append("--cxx={}".format(tools.get_env("CXX")))
        extra_cflags = []
        extra_ldflags = []
        if tools.is_apple_os(self.settings.os) and self.settings.os.version:
            extra_cflags.append(tools.apple_deployment_target_flag(self.settings.os, self.settings.os.version))
            extra_ldflags.append(tools.apple_deployment_target_flag(self.settings.os, self.settings.os.version))
        if self.settings.compiler == "Visual Studio":
            args.append("--pkg-config={}".format(tools.get_env("PKG_CONFIG")))
            args.append("--toolchain=msvc")
            if tools.Version(str(self.settings.compiler.version)) <= 12:
                # Visual Studio 2013 (and earlier) doesn't support "inline" keyword for C (only for C++)
                self._autotools.defines.append("inline=__inline")
        if tools.cross_building(self):
            args.append("--target-os={}".format(self._target_os))
            if tools.is_apple_os(self.settings.os):
                xcrun = tools.XCRun(self.settings)
                apple_arch = tools.to_apple_arch(str(self.settings.arch))
                extra_cflags.extend(["-arch {}".format(apple_arch), "-isysroot {}".format(xcrun.sdk_path)])
                extra_ldflags.extend(["-arch {}".format(apple_arch), "-isysroot {}".format(xcrun.sdk_path)])

        args.append("--extra-cflags={}".format(" ".join(extra_cflags)))
        args.append("--extra-ldflags={}".format(" ".join(extra_ldflags)))

        self._autotools.configure(args=args, configure_dir=self._source_subfolder, build=False, host=False, target=False)
        return self._autotools

    def build(self):
        self._patch_sources()
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                              "echo libx264.lib", "echo x264.lib")
        if self.options.with_libx264:
            shutil.copy("x264.pc", "libx264.pc")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                # ffmpeg created `.lib` files in the `/bin` folder
                for fn in os.listdir(os.path.join(self.package_folder, "bin")):
                    if fn.endswith(".lib"):
                        tools.rename(os.path.join(self.package_folder, "bin", fn),
                                     os.path.join(self.package_folder, "lib", fn))
                tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.def")
            else:
                # ffmpeg produces `.a` files that are actually `.lib` files
                with tools.chdir(os.path.join(self.package_folder, "lib")):
                    for lib in glob.glob("*.a"):
                        tools.rename(lib, lib[3:-2] + ".lib")

    def _read_component_version(self, component_name):
        result = dict()
        version_file_name = os.path.join(self.package_folder,
                                         "include", "lib%s" % component_name,
                                         "version.h")
        version_file = open(version_file_name, "r")
        pattern = "define LIB%s_VERSION_(MAJOR|MINOR|MICRO)[ \t]+(\\d+)" % (
                  component_name.upper())
        version = dict()
        for line in version_file:
            match = re.search(pattern, line)
            if match:
                version[match[1]] = match[2]
        if "MAJOR" in version and "MINOR" in version and "MICRO" in version:
            return f"{version['MAJOR']}.{version['MINOR']}.{version['MICRO']}"
        return None

    def _set_component_version(self, component_name):
        version = self._read_component_version(component_name)
        if version is not None:
            self.cpp_info.components[component_name].version = version
        else:
            self.output.warn("cannot determine version of "
                  "lib%s packaged with ffmpeg!" % component_name)

    def package_info(self):
        self.cpp_info.components["avdevice"].libs = ["avdevice"]
        self.cpp_info.components["avdevice"].requires = ["avfilter", "swscale", "avformat", "avcodec", "swresample", "avutil"]
        self.cpp_info.components["avdevice"].names["pkg_config"] = "libavdevice"
        self._set_component_version("avdevice")

        self.cpp_info.components["avfilter"].libs = ["avfilter"]
        self.cpp_info.components["avfilter"].requires = ["swscale", "avformat", "avcodec", "swresample", "avutil"]
        self.cpp_info.components["avfilter"].names["pkg_config"] = "libavfilter"
        self._set_component_version("avfilter")

        self.cpp_info.components["avformat"].libs = ["avformat"]
        self.cpp_info.components["avformat"].requires = ["avcodec", "swresample", "avutil"]
        self.cpp_info.components["avformat"].names["pkg_config"] = "libavformat"
        self._set_component_version("avformat")

        self.cpp_info.components["avcodec"].libs = ["avcodec"]
        self.cpp_info.components["avcodec"].requires = ["swresample", "avutil"]
        self.cpp_info.components["avcodec"].names["pkg_config"] = "libavcodec"
        self._set_component_version("avcodec")

        self.cpp_info.components["swscale"].libs = ["swscale"]
        self.cpp_info.components["swscale"].requires = ["avutil"]
        self.cpp_info.components["swscale"].names["pkg_config"] = "libswscale"
        self._set_component_version("swscale")

        self.cpp_info.components["swresample"].libs = ["swresample"]
        self.cpp_info.components["swresample"].names["pkg_config"] = "libswresample"
        self.cpp_info.components["swresample"].requires = ["avutil"]
        self._set_component_version("swresample")

        if self.options.postproc:
            self.cpp_info.components["postproc"].libs = ["postproc"]
            self.cpp_info.components["postproc"].requires = ["avutil"]
            self.cpp_info.components["postproc"].names["pkg_config"] = "libpostproc"
            self._set_component_version("postproc")

            self.cpp_info.components["avfilter"].requires.append("postproc")
            self.cpp_info.components["avdevice"].requires.append("postproc")

        self.cpp_info.components["avutil"].libs = ["avutil"]
        self.cpp_info.components["avutil"].names["pkg_config"] = "libavutil"
        self._set_component_version("avutil")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["avutil"].system_libs = ["pthread", "m", "dl"]
            self.cpp_info.components["swresample"].system_libs = ["m"]
            self.cpp_info.components["swscale"].system_libs = ["m"]
            if self.options.postproc:
                self.cpp_info.components["postproc"].system_libs = ["m"]
            if self.options.get_safe("fPIC"):
                if self.settings.compiler in ("gcc", ):
                    # https://trac.ffmpeg.org/ticket/1713
                    # https://ffmpeg.org/platform.html#Advanced-linking-configuration
                    # https://ffmpeg.org/pipermail/libav-user/2014-December/007719.html
                    self.cpp_info.components["avcodec"].exelinkflags.append("-Wl,-Bsymbolic")
                    self.cpp_info.components["avcodec"].sharedlinkflags.append("-Wl,-Bsymbolic")
            self.cpp_info.components["avformat"].system_libs = ["m"]
            self.cpp_info.components["avfilter"].system_libs = ["m", "pthread"]
            self.cpp_info.components["avdevice"].system_libs = ["m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["avcodec"].system_libs = ["Mfplat", "Mfuuid"]
            self.cpp_info.components["avdevice"].system_libs = ["ole32", "psapi", "strmiids", "uuid", "oleaut32", "shlwapi", "gdi32", "vfw32"]
            self.cpp_info.components["avutil"].system_libs = ["user32", "bcrypt"]
        elif tools.is_apple_os(self.settings.os):
            self.cpp_info.components["avdevice"].frameworks = ["CoreFoundation", "Foundation", "CoreGraphics"]
            self.cpp_info.components["avfilter"].frameworks = ["CoreGraphics"]
            self.cpp_info.components["avcodec"].frameworks = ["CoreVideo", "CoreMedia"]
            if self.settings.os == "Macos":
                self.cpp_info.components["avdevice"].frameworks.append("OpenGL")
                self.cpp_info.components["avfilter"].frameworks.append("OpenGL")

        if self.options.get_safe("with_libalsa"):
            self.cpp_info.components["avdevice"].requires.append("libalsa::libalsa")

        if self.options.get_safe("with_xcb"):
            self.cpp_info.components["avdevice"].requires.append("xorg::xcb")

        if self.options.get_safe("with_pulse"):
            self.cpp_info.components["avdevice"].requires.append("pulseaudio::pulseaudio")

        if self.options.with_zlib:
            self.cpp_info.components["avcodec"].requires.append("zlib::zlib")

        if self.options.with_bzip2:
            self.cpp_info.components["avformat"].requires.append("bzip2::bzip2")

        if self.options.with_lzma:
            self.cpp_info.components["avcodec"].requires.append("xz_utils::xz_utils")

        if self.options.with_libiconv:
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

        if self.options.with_libx264:
            self.cpp_info.components["avcodec"].requires.append("libx264::libx264")

        if self.options.with_libx265:
            self.cpp_info.components["avcodec"].requires.append("libx265::libx265")

        if self.options.with_libvpx:
            self.cpp_info.components["avcodec"].requires.append("libvpx::libvpx")

        if self.options.with_libmp3lame:
            self.cpp_info.components["avcodec"].requires.append("libmp3lame::libmp3lame")

        if self.options.with_libfdk_aac:
            self.cpp_info.components["avcodec"].requires.append("libfdk_aac::libfdk_aac")

        if self.options.with_libwebp:
            self.cpp_info.components["avcodec"].requires.append("libwebp::libwebp")

        if self.options.with_ssl == "openssl":
            self.cpp_info.components["avformat"].requires.append("openssl::ssl")
        elif self.options.with_ssl == "securetransport":
            self.cpp_info.components["avformat"].frameworks.append("Security")

        if self.options.get_safe("with_vaapi"):
            self.cpp_info.components["avutil"].requires.extend(["vaapi::vaapi", "xorg::x11"])

        if self.options.get_safe("with_vdpau"):
            self.cpp_info.components["avutil"].requires.append("vdpau::vdpau")

        if self.options.get_safe("with_appkit"):
            self.cpp_info.components["avdevice"].frameworks.append("AppKit")
            self.cpp_info.components["avfilter"].frameworks.append("AppKit")

        if self.options.get_safe("with_avfoundation"):
            self.cpp_info.components["avdevice"].frameworks.append("AVFoundation")

        if self.options.get_safe("with_coreimage"):
            self.cpp_info.components["avfilter"].frameworks.append("CoreImage")

        if self.options.get_safe("with_audiotoolbox"):
            self.cpp_info.components["avcodec"].frameworks.append("AudioToolbox")
            self.cpp_info.components["avdevice"].frameworks.append("CoreAudio")

        if self.options.get_safe("with_videotoolbox"):
            self.cpp_info.components["avcodec"].frameworks.append("VideoToolbox")

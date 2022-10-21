from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os, to_apple_arch
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps, get_gnu_triplet
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
from conans.tools import apple_deployment_target_flag, XCRun
import os
import glob
import re

required_conan_version = ">=1.52.0"

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
        "avdevice": [True, False],
        "avcodec": [True, False],
        "avformat": [True, False],
        "swresample": [True, False],
        "swscale": [True, False],
        "postproc": [True, False],
        "avfilter": [True, False],
        "with_asm": [True, False],
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
        "with_vulkan": [True, False],
        "with_xcb": [True, False],
        "with_appkit": [True, False],
        "with_avfoundation": [True, False],
        "with_coreimage": [True, False],
        "with_audiotoolbox": [True, False],
        "with_videotoolbox": [True, False],
        "with_programs": [True, False],
        "disable_everything": [True, False],
        "disable_all_encoders": [True, False],
        "disable_encoders": "ANY",
        "enable_encoders": "ANY",
        "disable_all_decoders": [True, False],
        "disable_decoders": "ANY",
        "enable_decoders": "ANY",
        "disable_all_hardware_accelerators": [True, False],
        "disable_hardware_accelerators": "ANY",
        "enable_hardware_accelerators": "ANY",
        "disable_all_muxers": [True, False],
        "disable_muxers": "ANY",
        "enable_muxers": "ANY",
        "disable_all_demuxers": [True, False],
        "disable_demuxers": "ANY",
        "enable_demuxers": "ANY",
        "disable_all_parsers": [True, False],
        "disable_parsers": "ANY",
        "enable_parsers": "ANY",
        "disable_all_bitstream_filters": [True, False],
        "disable_bitstream_filters": "ANY",
        "enable_bitstream_filters": "ANY",
        "disable_all_protocols": [True, False],
        "disable_protocols": "ANY",
        "enable_protocols": "ANY",
        "disable_all_devices": [True, False],
        "disable_all_input_devices": [True, False],
        "disable_input_devices": "ANY",
        "enable_input_devices": "ANY",
        "disable_all_output_devices": [True, False],
        "disable_output_devices": "ANY",
        "enable_output_devices": "ANY",
        "disable_all_filters": [True, False],
        "disable_filters": "ANY",
        "enable_filters": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "avdevice": True,
        "avcodec": True,
        "avformat": True,
        "swresample": True,
        "swscale": True,
        "postproc": True,
        "avfilter": True,
        "with_asm": True,
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
        "with_vulkan": True,
        "with_xcb": True,
        "with_appkit": True,
        "with_avfoundation": True,
        "with_coreimage": True,
        "with_audiotoolbox": True,
        "with_videotoolbox": True,
        "with_programs": True,
        "disable_everything": False,
        "disable_all_encoders": False,
        "disable_encoders": None,
        "enable_encoders": None,
        "disable_all_decoders": False,
        "disable_decoders": None,
        "enable_decoders": None,
        "disable_all_hardware_accelerators": False,
        "disable_hardware_accelerators": None,
        "enable_hardware_accelerators": None,
        "disable_all_muxers": False,
        "disable_muxers": None,
        "enable_muxers": None,
        "disable_all_demuxers": False,
        "disable_demuxers": None,
        "enable_demuxers": None,
        "disable_all_parsers": False,
        "disable_parsers": None,
        "enable_parsers": None,
        "disable_all_bitstream_filters": False,
        "disable_bitstream_filters": None,
        "enable_bitstream_filters": None,
        "disable_all_protocols": False,
        "disable_protocols": None,
        "enable_protocols": None,
        "disable_all_devices": False,
        "disable_all_input_devices": False,
        "disable_input_devices": None,
        "enable_input_devices": None,
        "disable_all_output_devices": False,
        "disable_output_devices": None,
        "enable_output_devices": None,
        "disable_all_filters": False,
        "disable_filters": None,
        "enable_filters": None,
    }

    @property
    def _dependencies(self):
        return {
            "avformat": ["avcodec"],
            "avdevice": ["avcodec", "avformat"],
            "avfilter": ["avformat"],
            "with_bzip2": ["avformat"],
            "with_ssl": ["avformat"],
            "with_zlib": ["avcodec"],
            "with_lzma": ["avcodec"],
            "with_libiconv": ["avcodec"],
            "with_openjpeg": ["avcodec"],
            "with_openh264": ["avcodec"],
            "with_vorbis": ["avcodec"],
            "with_opus": ["avcodec"],
            "with_libx264": ["avcodec"],
            "with_libx265": ["avcodec"],
            "with_libvpx": ["avcodec"],
            "with_libmp3lame": ["avcodec"],
            "with_libfdk_aac": ["avcodec"],
            "with_libwebp": ["avcodec"],
            "with_freetype": ["avfilter"],
            "with_zeromq": ["avfilter", "avformat"],
            "with_libalsa": ["avdevice"],
            "with_xcb": ["avdevice"],
            "with_pulse": ["avdevice"],
            "with_sdl": ["with_programs"],
        }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self.settings.os in ["Linux", "FreeBSD"]:
            del self.options.with_vaapi
            del self.options.with_vdpau
            del self.options.with_vulkan
            del self.options.with_xcb
            del self.options.with_libalsa
            del self.options.with_pulse
        if self.settings.os != "Macos":
            del self.options.with_appkit
        if self.settings.os not in ["Macos", "iOS", "tvOS"]:
            del self.options.with_coreimage
            del self.options.with_audiotoolbox
            del self.options.with_videotoolbox
        if not is_apple_os(self):
            del self.options.with_avfoundation
        if not self._version_supports_vulkan():
            del self.options.with_vulkan

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self)

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_libiconv:
            self.requires("libiconv/1.17")
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        if self.options.with_openh264:
            self.requires("openh264/2.1.1")
        if self.options.with_vorbis:
            self.requires("vorbis/1.3.7")
        if self.options.with_opus:
            self.requires("opus/1.3.1")
        if self.options.with_zeromq:
            self.requires("zeromq/4.3.4")
        if self.options.with_sdl:
            self.requires("sdl/2.0.20")
        if self.options.with_libx264:
            self.requires("libx264/20191217")
        if self.options.with_libx265:
            self.requires("libx265/3.4")
        if self.options.with_libvpx:
            self.requires("libvpx/1.11.0")
        if self.options.with_libmp3lame:
            self.requires("libmp3lame/3.100")
        if self.options.with_libfdk_aac:
            self.requires("libfdk_aac/2.0.2")
        if self.options.with_libwebp:
            self.requires("libwebp/1.2.3")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")
        if self.options.get_safe("with_libalsa"):
            self.requires("libalsa/1.2.7.2")
        if self.options.get_safe("with_xcb") or self.options.get_safe("with_vaapi"):
            self.requires("xorg/system")
        if self.options.get_safe("with_pulse"):
            self.requires("pulseaudio/14.2")
        if self.options.get_safe("with_vaapi"):
            self.requires("vaapi/system")
        if self.options.get_safe("with_vdpau"):
            self.requires("vdpau/system")
        if self._version_supports_vulkan() and self.options.get_safe("with_vulkan"):
            self.requires("vulkan-loader/1.3.221")

    def validate(self):
        if self.options.with_ssl == "securetransport" and not is_apple_os(self):
            raise ConanInvalidConfiguration(
                "securetransport is only available on Apple")

        for dependency, features in self._dependencies.items():
            if not self.options.get_safe(dependency):
                continue
            used = False
            for feature in features:
                used = used or self.options.get_safe(feature)
            if not used:
                dependency_string = "' or '".join(features)
                raise ConanInvalidConfiguration(f"FFmpeg '{dependency_string}' option requires '{dependency_string}' option to be enabled")

    def build_requirements(self):
        if self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("yasm/1.3.0")
        self.tool_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not self.win_bash:
            self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    @property
    def _target_arch(self):
        target_arch, _, _ = get_gnu_triplet._get_gnu_triplet(
            "Macos" if is_apple_os(self) else str(self.settings.os),
            str(self.settings.arch),
            str(self.settings.compiler) if self.settings.os == "Windows" else None,
        ).split("-")
        return target_arch

    @property
    def _target_os(self):
        if is_msvc(self):
            return "win32"
        else:
            _, _, target_os = get_gnu_triplet._get_gnu_triplet(
                "Macos" if is_apple_os(self) else str(self.settings.os),
                str(self.settings.arch),
                str(self.settings.compiler) if self.settings.os == "Windows" else None,
            ).split("-")
            if target_os == "gnueabihf":
                target_os = "gnu" # could also be "linux"
            return target_os

    def _patch_sources(self):
        if is_msvc(self) and self.options.with_libx264 and not self.options["libx264"].shared:
            # suppress MSVC linker warnings: https://trac.ffmpeg.org/ticket/7396
            # warning LNK4049: locally defined symbol x264_levels imported
            # warning LNK4049: locally defined symbol x264_bit_depth imported
            replace_in_file(self, os.path.join(self.source_folder, "libavcodec", "libx264.c"),
                                  "#define X264_API_IMPORTS 1", "")
        if self.options.with_ssl == "openssl":
            # https://trac.ffmpeg.org/ticket/5675
            openssl_libraries = " ".join(
                [f"-l{lib}" for lib in self.deps_cpp_info["openssl"].libs])
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                                  "check_lib openssl openssl/ssl.h SSL_library_init -lssl -lcrypto -lws2_32 -lgdi32 ||",
                                  f"check_lib openssl openssl/ssl.h OPENSSL_init_ssl {openssl_libraries} || ")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)

        def opt_enable_disable(what, v):
            action = "enable" if v else "disable"
            return f"--{action}-{what}"

        def opt_append_disable_if_set(args, what, v):
            if v:
                args.append(f"--disable-{what}")

        args = [
            "--pkg-config-flags=--static",
            "--disable-doc",
            opt_enable_disable("cross-compile", cross_building(self)),
            opt_enable_disable("asm", self.options.with_asm),
            # Libraries
            opt_enable_disable("pic", self.options.get_safe("fPIC", True)),
            # Components
            opt_enable_disable("avdevice", self.options.avdevice),
            opt_enable_disable("avcodec", self.options.avcodec),
            opt_enable_disable("avformat", self.options.avformat),
            opt_enable_disable("swresample", self.options.swresample),
            opt_enable_disable("swscale", self.options.swscale),
            opt_enable_disable("postproc", self.options.postproc),
            opt_enable_disable("avfilter", self.options.avfilter),

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
            opt_enable_disable(
                "libpulse", self.options.get_safe("with_pulse")),
            opt_enable_disable("vaapi", self.options.get_safe("with_vaapi")),
            opt_enable_disable("vdpau", self.options.get_safe("with_vdpau")),
            opt_enable_disable("libxcb", self.options.get_safe("with_xcb")),
            opt_enable_disable(
                "libxcb-shm", self.options.get_safe("with_xcb")),
            opt_enable_disable(
                "libxcb-shape", self.options.get_safe("with_xcb")),
            opt_enable_disable(
                "libxcb-xfixes", self.options.get_safe("with_xcb")),
            opt_enable_disable("appkit", self.options.get_safe("with_appkit")),
            opt_enable_disable(
                "avfoundation", self.options.get_safe("with_avfoundation")),
            opt_enable_disable(
                "coreimage", self.options.get_safe("with_coreimage")),
            opt_enable_disable(
                "audiotoolbox", self.options.get_safe("with_audiotoolbox")),
            opt_enable_disable(
                "videotoolbox", self.options.get_safe("with_videotoolbox")),
            opt_enable_disable("securetransport",
                               self.options.with_ssl == "securetransport"),
            "--disable-cuda",  # FIXME: CUDA support
            "--disable-cuvid",  # FIXME: CUVID support
            # Licenses
            opt_enable_disable("nonfree", self.options.with_libfdk_aac or (self.options.with_ssl and (
                self.options.with_libx264 or self.options.with_libx265 or self.options.postproc))),
            opt_enable_disable(
                "gpl", self.options.with_libx264 or self.options.with_libx265 or self.options.postproc)
        ]

        # Individual Component Options
        opt_append_disable_if_set(args, "everything", self.options.disable_everything)
        opt_append_disable_if_set(args, "encoders", self.options.disable_all_encoders)
        opt_append_disable_if_set(args, "decoders", self.options.disable_all_decoders)
        opt_append_disable_if_set(args, "hwaccels", self.options.disable_all_hardware_accelerators)
        opt_append_disable_if_set(args, "muxers", self.options.disable_all_muxers)
        opt_append_disable_if_set(args, "demuxers", self.options.disable_all_demuxers)
        opt_append_disable_if_set(args, "parsers", self.options.disable_all_parsers)
        opt_append_disable_if_set(args, "bsfs", self.options.disable_all_bitstream_filters)
        opt_append_disable_if_set(args, "protocols", self.options.disable_all_protocols)
        opt_append_disable_if_set(args, "devices", self.options.disable_all_devices)
        opt_append_disable_if_set(args, "indevs", self.options.disable_all_input_devices)
        opt_append_disable_if_set(args, "outdevs", self.options.disable_all_output_devices)
        opt_append_disable_if_set(args, "filters", self.options.disable_all_filters)

        args.extend(self._split_and_format_options_string(
            "enable-encoder", self.options.enable_encoders))
        args.extend(self._split_and_format_options_string(
            "disable-encoder", self.options.disable_encoders))
        args.extend(self._split_and_format_options_string(
            "enable-decoder", self.options.enable_decoders))
        args.extend(self._split_and_format_options_string(
            "disable-decoder", self.options.disable_decoders))
        args.extend(self._split_and_format_options_string(
            "enable-hwaccel", self.options.enable_hardware_accelerators))
        args.extend(self._split_and_format_options_string(
            "disable-hwaccel", self.options.disable_hardware_accelerators))
        args.extend(self._split_and_format_options_string(
            "enable-muxer", self.options.enable_muxers))
        args.extend(self._split_and_format_options_string(
            "disable-muxer", self.options.disable_muxers))
        args.extend(self._split_and_format_options_string(
            "enable-demuxer", self.options.enable_demuxers))
        args.extend(self._split_and_format_options_string(
            "disable-demuxer", self.options.disable_demuxers))
        args.extend(self._split_and_format_options_string(
            "enable-parser", self.options.enable_parsers))
        args.extend(self._split_and_format_options_string(
            "disable-parser", self.options.disable_parsers))
        args.extend(self._split_and_format_options_string(
            "enable-bsf", self.options.enable_bitstream_filters))
        args.extend(self._split_and_format_options_string(
            "disable-bsf", self.options.disable_bitstream_filters))
        args.extend(self._split_and_format_options_string(
            "enable-protocol", self.options.enable_protocols))
        args.extend(self._split_and_format_options_string(
            "disable-protocol", self.options.disable_protocols))
        args.extend(self._split_and_format_options_string(
            "enable-indev", self.options.enable_input_devices))
        args.extend(self._split_and_format_options_string(
            "disable-indev", self.options.disable_input_devices))
        args.extend(self._split_and_format_options_string(
            "enable-outdev", self.options.enable_output_devices))
        args.extend(self._split_and_format_options_string(
            "disable-outdev", self.options.disable_output_devices))
        args.extend(self._split_and_format_options_string(
            "enable-filter", self.options.enable_filters))
        args.extend(self._split_and_format_options_string(
            "disable-filter", self.options.disable_filters))

        if self._version_supports_vulkan():
            args.append(opt_enable_disable(
                "vulkan", self.options.get_safe("with_vulkan")))
        if is_apple_os(self):
            # relocatable shared libs
            args.append("--install-name-dir=@rpath")
        args.append(f"--arch={self._target_arch}")
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
        as_value = os.getenv("AX")
        if as_value:
            args.append(f"--as={as_value}")
        cc_value = os.getenv("CC")
        if cc_value:
            args.append(f"--cc={cc_value}")
        cxx = os.getenv("CXX")
        if cxx:
            args.append(f"--cxx={cxx}")
        extra_cflags = []
        extra_ldflags = []
        if is_apple_os(self) and self.settings.os.version:
            extra_cflags.append(apple_deployment_target_flag(
                self.settings.os, self.settings.os.version))
            extra_ldflags.append(apple_deployment_target_flag(
                self.settings.os, self.settings.os.version))
        if is_msvc(self):
            pkg_config = os.getenv("PKG_CONFIG")
            args.append(f"--pkg-config={pkg_config}")
            args.append("--toolchain=msvc")
            if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) <= "12":
                # Visual Studio 2013 (and earlier) doesn't support "inline" keyword for C (only for C++)
                tc.defines.append("inline=__inline")
        if cross_building(self):
            if self._target_os == "emscripten":
                args.append("--target-os=none")
            else:
                args.append(f"--target-os={self._target_os}")

            if is_apple_os(self):
                if self.options.with_audiotoolbox:
                    args.append("--disable-outdev=audiotoolbox")

                xcrun = XCRun(self.settings)
                apple_arch = to_apple_arch(self)
                extra_cflags.extend(
                    [f"-arch {apple_arch}", f"-isysroot {xcrun.sdk_path}"])
                extra_ldflags.extend(
                    [f"-arch {apple_arch}", f"-isysroot {xcrun.sdk_path}"])

        extra_cflags_string = " ".join(extra_cflags)
        args.append(f"--extra-cflags={extra_cflags_string}")
        extra_ldflags_string = " ".join(extra_ldflags)
        args.append(f"--extra-ldflags={extra_ldflags_string}")

        # FIXME: This is a hack that feels wrong but I don't know how to fix properly. Is this an AutotoolsTolchain
        #  problem
        del tc.configure_args[7] # --oldincludedir=${prefix}/include
        del tc.configure_args[6] # --includedir=${prefix}/include
        del tc.configure_args[4] # --sbin=${prefix}/bin
        tc.configure_args.append("--incdir=${prefix}/include")

        tc.configure_args.extend(args)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def _split_and_format_options_string(self, flag_name, options_list):
        if not options_list:
            return []

        def _format_options_list_item(flag_name, options_item):
            return f"--{flag_name}={options_item}"

        def _split_options_string(options_string):
            return list(filter(None, "".join(options_string.split()).split(",")))

        options_string = str(options_list)
        return [_format_options_list_item(flag_name, item) for item in _split_options_string(options_string)]

    def build(self):
        self._patch_sources()
        replace_in_file(self, os.path.join(self.source_folder, "configure"),
                              "echo libx264.lib", "echo x264.lib")
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        if is_msvc(self):
            if self.options.shared:
                # ffmpeg created `.lib` files in the `/bin` folder
                for fn in os.listdir(os.path.join(self.package_folder, "bin")):
                    if fn.endswith(".lib"):
                        rename(self, os.path.join(self.package_folder, "bin", fn),
                               os.path.join(self.package_folder, "lib", fn))
                rm(self, "*.def", os.path.join(self.package_folder, "lib"))
            else:
                # ffmpeg produces `.a` files that are actually `.lib` files
                with chdir(self, os.path.join(self.package_folder, "lib")):
                    for lib in glob.glob("*.a"):
                        rename(self, lib, lib[3:-2] + ".lib")

        fix_apple_shared_install_name(self)

    def _read_component_version(self, component_name):
        version_file_name = os.path.join(self.package_folder,
                                         "include", f"lib{component_name}",
                                         "version.h")
        with open(version_file_name, "r", encoding="utf8") as version_file:
            pattern = f"define LIB{component_name.upper()}_VERSION_(MAJOR|MINOR|MICRO)[ \t]+(\\d+)"
            version = {}
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
                             f"lib{component_name} packaged with ffmpeg!")

    def package_info(self):
        if self.options.with_programs:
            if self.options.with_sdl:
                self.cpp_info.components["programs"].requires = [
                    "sdl::libsdl2"]

        if self.options.avdevice:
            self.cpp_info.components["avdevice"].set_property(
                "pkg_config_name", "libavdevice")
            self.cpp_info.components["avdevice"].libs = ["avdevice"]
            self.cpp_info.components["avdevice"].requires = ["avutil"]
            if self.options.avfilter:
                self.cpp_info.components["avdevice"].requires.append(
                    "avfilter")
            if self.options.swscale:
                self.cpp_info.components["avdevice"].requires.append("swscale")
            if self.options.avformat:
                self.cpp_info.components["avdevice"].requires.append(
                    "avformat")
            if self.options.avcodec:
                self.cpp_info.components["avdevice"].requires.append("avcodec")
            if self.options.swresample:
                self.cpp_info.components["avdevice"].requires.append(
                    "swresample")
            if self.options.postproc:
                self.cpp_info.components["avdevice"].requires.append(
                    "postproc")
            self._set_component_version("avdevice")

        if self.options.avfilter:
            self.cpp_info.components["avfilter"].set_property(
                "pkg_config_name", "libavfilter")
            self.cpp_info.components["avfilter"].libs = ["avfilter"]
            self.cpp_info.components["avfilter"].requires = ["avutil"]
            if self.options.swscale:
                self.cpp_info.components["avfilter"].requires.append("swscale")
            if self.options.avformat:
                self.cpp_info.components["avfilter"].requires.append(
                    "avformat")
            if self.options.avcodec:
                self.cpp_info.components["avfilter"].requires.append("avcodec")
            if self.options.swresample:
                self.cpp_info.components["avfilter"].requires.append(
                    "swresample")
            if self.options.postproc:
                self.cpp_info.components["avfilter"].requires.append(
                    "postproc")
            self._set_component_version("avfilter")

        if self.options.avformat:
            self.cpp_info.components["avformat"].set_property(
                "pkg_config_name", "libavformat")
            self.cpp_info.components["avformat"].libs = ["avformat"]
            self.cpp_info.components["avformat"].requires = ["avutil"]
            if self.options.avcodec:
                self.cpp_info.components["avformat"].requires.append("avcodec")
            if self.options.swresample:
                self.cpp_info.components["avformat"].requires.append(
                    "swresample")
            self._set_component_version("avformat")

        if self.options.avcodec:
            self.cpp_info.components["avcodec"].set_property(
                "pkg_config_name", "libavcodec")
            self.cpp_info.components["avcodec"].libs = ["avcodec"]
            self.cpp_info.components["avcodec"].requires = ["avutil"]
            if self.options.swresample:
                self.cpp_info.components["avcodec"].requires.append(
                    "swresample")
            self._set_component_version("avcodec")

        if self.options.swscale:
            self.cpp_info.components["swscale"].set_property(
                "pkg_config_name", "libswscale")
            self.cpp_info.components["swscale"].libs = ["swscale"]
            self.cpp_info.components["swscale"].requires = ["avutil"]
            self._set_component_version("swscale")

        if self.options.swresample:
            self.cpp_info.components["swresample"].set_property(
                "pkg_config_name", "libswresample")
            self.cpp_info.components["swresample"].libs = ["swresample"]
            self.cpp_info.components["swresample"].requires = ["avutil"]
            self._set_component_version("swresample")

        if self.options.postproc:
            self.cpp_info.components["postproc"].set_property(
                "pkg_config_name", "libpostproc")
            self.cpp_info.components["postproc"].libs = ["postproc"]
            self.cpp_info.components["postproc"].requires = ["avutil"]
            self._set_component_version("postproc")

        self.cpp_info.components["avutil"].set_property(
            "pkg_config_name", "libavutil")
        self.cpp_info.components["avutil"].libs = ["avutil"]
        self._set_component_version("avutil")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["avutil"].system_libs = [
                "pthread", "m", "dl"]
            if self.options.swresample:
                self.cpp_info.components["swresample"].system_libs = ["m"]
            if self.options.swscale:
                self.cpp_info.components["swscale"].system_libs = ["m"]
            if self.options.postproc:
                self.cpp_info.components["postproc"].system_libs = ["m"]
            if self.options.get_safe("fPIC"):
                if self.settings.compiler in ("gcc", "clang"):
                    # https://trac.ffmpeg.org/ticket/1713
                    # https://ffmpeg.org/platform.html#Advanced-linking-configuration
                    # https://ffmpeg.org/pipermail/libav-user/2014-December/007719.html
                    self.cpp_info.components["avcodec"].exelinkflags.append(
                        "-Wl,-Bsymbolic")
                    self.cpp_info.components["avcodec"].sharedlinkflags.append(
                        "-Wl,-Bsymbolic")
            if self.options.avformat:
                self.cpp_info.components["avformat"].system_libs = ["m"]
            if self.options.avfilter:
                self.cpp_info.components["avfilter"].system_libs = [
                    "m", "pthread"]
            if self.options.avdevice:
                self.cpp_info.components["avdevice"].system_libs = ["m"]
        elif self.settings.os == "Windows":
            if self.options.avcodec:
                self.cpp_info.components["avcodec"].system_libs = [
                    "Mfplat", "Mfuuid", "strmiids"]
            if self.options.avdevice:
                self.cpp_info.components["avdevice"].system_libs = [
                    "ole32", "psapi", "strmiids", "uuid", "oleaut32", "shlwapi", "gdi32", "vfw32"]
            self.cpp_info.components["avutil"].system_libs = [
                "user32", "bcrypt"]
            self.cpp_info.components["avformat"].system_libs = ["secur32"]
        elif is_apple_os(self):
            if self.options.avdevice:
                self.cpp_info.components["avdevice"].frameworks = [
                    "CoreFoundation", "Foundation", "CoreGraphics"]
            if self.options.avfilter:
                self.cpp_info.components["avfilter"].frameworks = [
                    "CoreGraphics"]
            if self.options.avcodec:
                self.cpp_info.components["avcodec"].frameworks = [
                    "CoreFoundation", "CoreVideo", "CoreMedia"]
            if self.settings.os == "Macos":
                if self.options.avdevice:
                    self.cpp_info.components["avdevice"].frameworks.append(
                        "OpenGL")
                if self.options.avfilter:
                    self.cpp_info.components["avfilter"].frameworks.append(
                        "OpenGL")

        if self.options.avdevice:
            if self.options.get_safe("with_libalsa"):
                self.cpp_info.components["avdevice"].requires.append(
                    "libalsa::libalsa")
            if self.options.get_safe("with_xcb"):
                self.cpp_info.components["avdevice"].requires.append(
                    "xorg::xcb")
            if self.options.get_safe("with_pulse"):
                self.cpp_info.components["avdevice"].requires.append(
                    "pulseaudio::pulseaudio")
            if self.options.get_safe("with_appkit"):
                self.cpp_info.components["avdevice"].frameworks.append(
                    "AppKit")
            if self.options.get_safe("with_avfoundation"):
                self.cpp_info.components["avdevice"].frameworks.append(
                    "AVFoundation")
            if self.options.get_safe("with_audiotoolbox"):
                self.cpp_info.components["avdevice"].frameworks.append(
                    "CoreAudio")

        if self.options.avcodec:
            if self.options.with_zlib:
                self.cpp_info.components["avcodec"].requires.append(
                    "zlib::zlib")
            if self.options.with_lzma:
                self.cpp_info.components["avcodec"].requires.append(
                    "xz_utils::xz_utils")
            if self.options.with_libiconv:
                self.cpp_info.components["avcodec"].requires.append(
                    "libiconv::libiconv")
            if self.options.with_openjpeg:
                self.cpp_info.components["avcodec"].requires.append(
                    "openjpeg::openjpeg")
            if self.options.with_openh264:
                self.cpp_info.components["avcodec"].requires.append(
                    "openh264::openh264")
            if self.options.with_vorbis:
                self.cpp_info.components["avcodec"].requires.append(
                    "vorbis::vorbis")
            if self.options.with_opus:
                self.cpp_info.components["avcodec"].requires.append(
                    "opus::opus")
            if self.options.with_libx264:
                self.cpp_info.components["avcodec"].requires.append(
                    "libx264::libx264")
            if self.options.with_libx265:
                self.cpp_info.components["avcodec"].requires.append(
                    "libx265::libx265")
            if self.options.with_libvpx:
                self.cpp_info.components["avcodec"].requires.append(
                    "libvpx::libvpx")
            if self.options.with_libmp3lame:
                self.cpp_info.components["avcodec"].requires.append(
                    "libmp3lame::libmp3lame")
            if self.options.with_libfdk_aac:
                self.cpp_info.components["avcodec"].requires.append(
                    "libfdk_aac::libfdk_aac")
            if self.options.with_libwebp:
                self.cpp_info.components["avcodec"].requires.append(
                    "libwebp::libwebp")
            if self.options.get_safe("with_audiotoolbox"):
                self.cpp_info.components["avcodec"].frameworks.append(
                    "AudioToolbox")
            if self.options.get_safe("with_videotoolbox"):
                self.cpp_info.components["avcodec"].frameworks.append(
                    "VideoToolbox")

        if self.options.avformat:
            if self.options.with_bzip2:
                self.cpp_info.components["avformat"].requires.append(
                    "bzip2::bzip2")
            if self.options.with_zeromq:
                self.cpp_info.components["avformat"].requires.append(
                    "zeromq::libzmq")
            if self.options.with_ssl == "openssl":
                self.cpp_info.components["avformat"].requires.append(
                    "openssl::ssl")
            elif self.options.with_ssl == "securetransport":
                self.cpp_info.components["avformat"].frameworks.append(
                    "Security")

        if self.options.avfilter:
            if self.options.with_freetype:
                self.cpp_info.components["avfilter"].requires.append(
                    "freetype::freetype")
            if self.options.with_zeromq:
                self.cpp_info.components["avfilter"].requires.append(
                    "zeromq::libzmq")
            if self.options.get_safe("with_appkit"):
                self.cpp_info.components["avfilter"].frameworks.append(
                    "AppKit")
            if self.options.get_safe("with_coreimage"):
                self.cpp_info.components["avfilter"].frameworks.append(
                    "CoreImage")
            if Version(self.version) >= "5.0" and is_apple_os(self):
                self.cpp_info.components["avfilter"].frameworks.append("Metal")

        if self.options.get_safe("with_vaapi"):
            self.cpp_info.components["avutil"].requires.extend(
                ["vaapi::vaapi", "xorg::x11"])

        if self.options.get_safe("with_vdpau"):
            self.cpp_info.components["avutil"].requires.append("vdpau::vdpau")

        if self._version_supports_vulkan() and self.options.get_safe("with_vulkan"):
            self.cpp_info.components["avutil"].requires.append(
                "vulkan-loader::vulkan-loader")

    def _version_supports_vulkan(self):
        return Version(self.version) >= "4.3.0"

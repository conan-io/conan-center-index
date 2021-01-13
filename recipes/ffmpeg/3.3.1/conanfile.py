#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import glob
import shutil


class FFMpegConan(ConanFile):
    name = "ffmpeg"
    version = "3.3.1"
    url = "https://github.com/bincrafters/conan-ffmpeg"
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    # https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md
    license = "LGPL-2.1-or-later", "GPL-2.0-or-later"
    homepage = "https://ffmpeg.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    topics = "ffmpeg", "multimedia", "audio", "video", "encoder", "decoder", "encoding", "decoding",\
             "transcoding", "multiplexer", "demultiplexer", "streaming"
    exports_sources = ["LICENSE"]
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
    default_options = {'shared': True,
                       'fPIC': True,
                       'postproc': False,
                       'zlib': True,
                       'bzlib': True,
                       'lzma': True,
                       'iconv': False,
                       'freetype': False,
                       'openjpeg': False,
                       'openh264': True,
                       'opus': False,
                       'vorbis': False,
                       'zmq': False,
                       'sdl2': False,
                       'x264': False,
                       'x265': False,
                       'vpx': False,
                       'mp3lame': False,  # Most probably I'll need to enable this
                       'fdk_aac': False,
                       'webp': False,
                       'openssl': False,
                       'alsa': True,
                       'pulse': True,
                       'vaapi': True,
                       'vdpau': True,
                       'xcb': True,
                       'appkit': True,
                       'avfoundation': True,
                       'coreimage': True,
                       'audiotoolbox': True,
                       'videotoolbox': True,
                       'securetransport': True,  # conflicts with OpenSSL
                       'qsv': True}
    generators = "pkg_config"
    _source_subfolder = "source_subfolder"

    @property
    def _is_mingw_windows(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc' and os.name == 'nt'

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            self.options.remove("vaapi")
            self.options.remove("vdpau")
            self.options.remove("xcb")
            self.options.remove("alsa")
            self.options.remove("pulse")
        if self.settings.os != "Macos":
            self.options.remove("appkit")
            self.options.remove("avfoundation")
            self.options.remove("coreimage")
            self.options.remove("audiotoolbox")
            self.options.remove("videotoolbox")
            self.options.remove("securetransport")
        if self.settings.os != "Windows":
            self.options.remove("qsv")

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")
        if self.settings.os == 'Windows' and "CONAN_MSYS_PATH" not in os.environ:
            self.build_requires("msys2/20200517")

    def requirements(self):
        if self.options.zlib:
            self.requires.add("zlib/1.2.11")
        if self.options.bzlib:
            self.requires.add("bzip2/1.0.8")
        if self.options.lzma:
            self.requires.add("xz_utils/5.2.4")
        if self.options.iconv:
            self.requires.add("libiconv/1.15")
        if self.options.freetype:
            self.requires.add("freetype/2.9.0")
        if self.options.openjpeg:
            self.requires.add("openjpeg/2.3.0")
        if self.options.openh264:
            self.requires.add("openh264/1.7.0")
        if self.options.vorbis:
            self.requires.add("vorbis/1.3.6")
        if self.options.opus:
            self.requires.add("opus/1.2.1")
        if self.options.zmq:
            self.requires.add("zmq/4.2.2")
        if self.options.sdl2:
            self.requires.add("sdl2/2.0.7")
        if self.options.x264:
            self.requires.add("libx264/20171211")
        if self.options.x265:
            self.requires.add("libx265/2.7")
        if self.options.vpx:
            self.requires.add("libvpx/1.7.0")
        if self.options.mp3lame:
            self.requires.add("libmp3lame/3.100")
        if self.options.fdk_aac:
            self.requires.add("libfdk_aac/0.1.5")
        if self.options.webp:
            self.requires.add("libwebp/1.0.0")
        if self.options.openssl:
            self.requires.add("OpenSSL/1.1.1b")
        if self.settings.os == "Linux":
            if self.options.vaapi:
                self.requires.add("libva/1.5.1")
        if self.settings.os == "Windows":
            if self.options.qsv:
                self.requires.add("intel_media_sdk/2018R2_1")

    def system_requirements(self):
        if self.settings.os == "Linux" and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                arch_suffix = ''
                if self.settings.arch == "x86":
                    arch_suffix = ':i386'
                elif self.settings.arch == "x86_64":
                    arch_suffix = ':amd64'

                packages = ['pkg-config']
                if self.options.alsa:
                    packages.append('libasound2-dev%s' % arch_suffix)
                if self.options.pulse:
                    packages.append('libpulse-dev%s' % arch_suffix)
                if self.options.vdpau:
                    packages.append('libvdpau-dev%s' % arch_suffix)
                if self.options.xcb:
                    packages.extend(['libxcb1-dev%s' % arch_suffix,
                                     'libxcb-shm0-dev%s' % arch_suffix,
                                     'libxcb-shape0-dev%s' % arch_suffix,
                                     'libxcb-xfixes0-dev%s' % arch_suffix])
                for package in packages:
                    installer.install(package)

    def _patch_sources(self):
        if self._is_msvc and self.options.x264 and not self.options['x264'].shared:
            # suppress MSVC linker warnings: https://trac.ffmpeg.org/ticket/7396
            # warning LNK4049: locally defined symbol x264_levels imported
            # warning LNK4049: locally defined symbol x264_bit_depth imported
            tools.replace_in_file(os.path.join(self._source_subfolder, 'libavcodec', 'libx264.c'),
                                  '#define X264_API_IMPORTS 1', '')
        if self.options.openssl and False: # v.looze: this patch is not needed for ffmpeg 3.3.1
            # https://trac.ffmpeg.org/ticket/5675
            openssl_libraries = ' '.join(['-l%s' % lib for lib in self.deps_cpp_info["OpenSSL"].libs])
            tools.replace_in_file(os.path.join(self._source_subfolder, 'configure'),
                                  'check_lib openssl openssl/ssl.h SSL_library_init -lssl -lcrypto -lws2_32 -lgdi32 ||',
                                  'check_lib openssl openssl/ssl.h OPENSSL_init_ssl %s || ' % openssl_libraries)

    def build(self):
        self._patch_sources()
        if self._is_msvc or self._is_mingw_windows:
            if "CONAN_MSYS_PATH" in os.environ:
                msys_bin = os.environ["CONAN_MSYS_PATH"]
            else:
                msys_bin = self.deps_env_info['msys2'].MSYS_BIN
            with tools.environment_append({'PATH': [msys_bin],
                                           'CONAN_BASH_PATH': os.path.join(msys_bin, 'bash.exe')}):
                if self._is_msvc:
                    with tools.vcvars(self.settings):
                        self.build_configure()
                else:
                    self.build_configure()
        else:
            self.build_configure()

    def build_configure(self):
        with tools.chdir(self._source_subfolder):
            prefix = tools.unix_path(self.package_folder) if self.settings.os == 'Windows' else self.package_folder
            args = ['--prefix=%s' % prefix,
                    '--disable-doc',
                    '--disable-programs']
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            args.append('--pkg-config-flags=--static')
            if self.settings.build_type == 'Debug':
                args.extend(['--disable-optimizations', '--disable-mmx', '--disable-stripping', '--enable-debug'])
            if self._is_msvc:
                args.append('--toolchain=msvc')
                args.append('--extra-cflags=-%s' % self.settings.compiler.runtime)
                if int(str(self.settings.compiler.version)) <= 12:
                    # Visual Studio 2013 (and earlier) doesn't support "inline" keyword for C (only for C++)
                    args.append('--extra-cflags=-Dinline=__inline' % self.settings.compiler.runtime)

            if self.settings.arch == 'x86':
                args.append('--arch=x86')

            if self.settings.os != "Windows":
                args.append('--enable-pic' if self.options.fPIC else '--disable-pic')

            args.append('--enable-postproc' if self.options.postproc else '--disable-postproc')
            args.append('--enable-zlib' if self.options.zlib else '--disable-zlib')
            args.append('--enable-bzlib' if self.options.bzlib else '--disable-bzlib')
            args.append('--enable-lzma' if self.options.lzma else '--disable-lzma')
            args.append('--enable-iconv' if self.options.iconv else '--disable-iconv')
            args.append('--enable-libfreetype' if self.options.freetype else '--disable-libfreetype')
            args.append('--enable-libopenjpeg' if self.options.openjpeg else '--disable-libopenjpeg')
            args.append('--enable-libopenh264' if self.options.openh264 else '--disable-libopenh264')
            args.append('--enable-libvorbis' if self.options.vorbis else '--disable-libvorbis')
            args.append('--enable-libopus' if self.options.opus else '--disable-libopus')
            args.append('--enable-libzmq' if self.options.zmq else '--disable-libzmq')
            args.append('--enable-sdl2' if self.options.sdl2 else '--disable-sdl2')
            args.append('--enable-libx264' if self.options.x264 else '--disable-libx264')
            args.append('--enable-libx265' if self.options.x265 else '--disable-libx265')
            args.append('--enable-libvpx' if self.options.vpx else '--disable-libvpx')
            args.append('--enable-libmp3lame' if self.options.mp3lame else '--disable-libmp3lame')
            args.append('--enable-libfdk-aac' if self.options.fdk_aac else '--disable-libfdk-aac')
            args.append('--enable-libwebp' if self.options.webp else '--disable-libwebp')
            args.append('--enable-openssl' if self.options.openssl else '--disable-openssl')

            #if self.options.x264 or self.options.x265 or self.options.postproc:
            #    args.append('--enable-gpl')
            assert not (self.options.x264 or self.options.x265 or self.options.postproc)
            args.append('--disable-gpl')

            # NOTE(a.kamyshev): Commented out lines are wrong, fdk_aac with lgpl does not require nonfree, it does so only for gpl license,
            # see https://www.ffmpeg.org/general.html#toc-OpenCORE_002c-VisualOn_002c-and-Fraunhofer-libraries
            #if self.options.fdk_aac:
            #    args.append('--enable-nonfree')
            args.append('--disable-nonfree')

            if self.settings.os == "Linux":
                # there is no option associated with alsa in ffmpeg 3.3.1
                # args.append('--enable-alsa' if self.options.alsa else '--disable-alsa')
                args.append('--enable-libpulse' if self.options.pulse else '--disable-libpulse')
                args.append('--enable-vaapi' if self.options.vaapi else '--disable-vaapi')
                args.append('--enable-vdpau' if self.options.vdpau else '--disable-vdpau')
                if self.options.xcb:
                    args.extend(['--enable-libxcb', '--enable-libxcb-shm',
                                 '--enable-libxcb-shape', '--enable-libxcb-xfixes'])
                else:
                    args.extend(['--disable-libxcb', '--disable-libxcb-shm',
                                 '--disable-libxcb-shape', '--disable-libxcb-xfixes'])

            if self.settings.os == "Macos" and False: # v.looze: ffmpeg 3.3.1 does not support these config options
                args.append('--enable-appkit' if self.options.appkit else '--disable-appkit')
                args.append('--enable-avfoundation' if self.options.avfoundation else '--disable-avfoundation')
                args.append('--enable-coreimage' if self.options.avfoundation else '--disable-coreimage')
                args.append('--enable-audiotoolbox' if self.options.audiotoolbox else '--disable-audiotoolbox')
                args.append('--enable-videotoolbox' if self.options.videotoolbox else '--disable-videotoolbox')
                args.append('--enable-securetransport' if self.options.securetransport else '--disable-securetransport')

            if self.settings.os == "Windows":
                args.append('--enable-libmfx' if self.options.qsv else '--disable-libmfx')

            # FIXME disable CUDA and CUVID by default, revisit later
            args.extend(['--disable-cuda', '--disable-cuvid'])

            # thanks to generators = "pkg_config", we will have all dependency
            # *.pc files in build folder, so pointing pkg-config there is enough
            pkg_config_path = os.path.abspath(self.build_folder)
            print("pkg_config_path or build_folder: " + pkg_config_path)
            pkg_config_path = tools.unix_path(pkg_config_path) if self.settings.os == 'Windows' else pkg_config_path

            try:
                if self._is_msvc or self._is_mingw_windows:
                    # hack for MSYS2 which doesn't inherit PKG_CONFIG_PATH
                    for filename in ['.bashrc', '.bash_profile', '.profile']:
                        tools.run_in_windows_bash(self, 'cp ~/%s ~/%s.bak' % (filename, filename))
                        command = 'echo "export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:%s" >> ~/%s'\
                                  % (pkg_config_path, filename)
                        tools.run_in_windows_bash(self, command)

                    # looks like msys2 package has pkg-config preinstalled,
                    # but we need to install it ourselves in case the msys in CONAN_MSYS_PATH does not have it
                    pkg_config_find_or_install_command = "pacman -Qs pkg-config || pacman -S --noconfirm pkg-config"
                    tools.run_in_windows_bash(self, pkg_config_find_or_install_command)

                    # intel_media_sdk.pc contains info on a package libmfx, but ffmpeg's configure script doesn't recognize it
                    tools.run_in_windows_bash(self, 'mv %s/intel_media_sdk.pc %s/libmfx.pc' % (pkg_config_path, pkg_config_path))

                env_build = AutoToolsBuildEnvironment(self, win_bash=self._is_mingw_windows or self._is_msvc)
                if self.settings.os == "Windows" and self.settings.build_type == "Debug":
                    # see https://trac.ffmpeg.org/ticket/6429 (ffmpeg does not build without compiler optimizations)
                    env_build.flags = ["-Zi", "-O2"]
                # ffmpeg's configure is not actually from autotools, so it doesn't understand standard options like
                # --host, --build, --target
                env_build.configure(args=args, build=False, host=False, target=False,
                    pkg_config_paths=[pkg_config_path])
                env_build.make()
                env_build.make(args=['install'])
            finally:
                if self._is_msvc or self._is_mingw_windows:
                    for filename in ['.bashrc', '.bash_profile', '.profile']:
                        tools.run_in_windows_bash(self, 'cp ~/%s.bak ~/%s' % (filename, filename))
                        tools.run_in_windows_bash(self, 'rm -f ~/%s.bak' % filename)

    def package(self):
        with tools.chdir(self._source_subfolder):
            self.copy(pattern="LICENSE")
        if self._is_msvc and not self.options.shared:
            # ffmpeg produces .a files which are actually .lib files
            with tools.chdir(os.path.join(self.package_folder, 'lib')):
                libs = glob.glob('*.a')
                for lib in libs:
                    shutil.move(lib, lib[:-2] + '.lib')

    def package_info(self):
        libs = [
            'avdevice',
            'avfilter',
            'avformat',
            'swresample',
            'swscale',
            'avcodec',
            'avutil'
        ]
        if self.options.postproc:
            libs.append('postproc')
        if self._is_msvc:
            if self.options.shared:
                self.cpp_info.libs = libs
                self.cpp_info.libdirs.append('bin')
            else:
                self.cpp_info.libs = ['lib' + lib for lib in libs]
        else:
            self.cpp_info.libs = libs
        if self.settings.os == "Macos":
            frameworks = ['CoreVideo', 'CoreMedia', 'CoreGraphics', 'CoreFoundation', 'OpenGL', 'Foundation', 'VideoDecodeAcceleration']
            if self.options.appkit:
                frameworks.append('AppKit')
            if self.options.avfoundation:
                frameworks.append('AVFoundation')
            if self.options.coreimage:
                frameworks.append('CoreImage')
            if self.options.audiotoolbox:
                frameworks.append('AudioToolbox')
            if self.options.videotoolbox:
                frameworks.append('VideoToolbox')
            if self.options.securetransport:
                frameworks.append('Security')
            for framework in frameworks:
                self.cpp_info.exelinkflags.append("-framework %s" % framework)
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['dl', 'pthread'])
            if self.options.alsa:
                self.cpp_info.system_libs.append('asound')
            if self.options.pulse:
                self.cpp_info.system_libs.append('pulse')
            if self.options.vdpau:
                self.cpp_info.system_libs.extend(['vdpau', 'X11'])
            if self.options.xcb:
                # FIXME: should instead rely on the same xcb as libva from Conan
                # self.cpp_info.system_libs.extend(['xcb', 'xcb-shm', 'xcb-shape', 'xcb-xfixes'])
                raise NotImplementedError()
            if self.settings.os != "Windows" and self.options.fPIC:
                # https://trac.ffmpeg.org/ticket/1713
                # https://ffmpeg.org/platform.html#Advanced-linking-configuration
                # https://ffmpeg.org/pipermail/libav-user/2014-December/007719.html
                self.cpp_info.sharedlinkflags.append("-Wl,-Bsymbolic")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(['ws2_32', 'secur32', 'shlwapi', 'strmiids', 'vfw32', 'bcrypt'])

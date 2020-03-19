from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)

        cmake.definitions['WITH_POSTPROC'] = self.options['ffmpeg'].postproc
        cmake.definitions['WITH_OPENJPEG'] = self.options['ffmpeg'].openjpeg
        cmake.definitions['WITH_OPENH264'] = self.options['ffmpeg'].openh264
        cmake.definitions['WITH_FREETYPE'] = self.options['ffmpeg'].freetype
        cmake.definitions['WITH_VORBIS'] = self.options['ffmpeg'].vorbis
        cmake.definitions['WITH_OPUS'] = self.options['ffmpeg'].opus
        cmake.definitions['WITH_ZMQ'] = self.options['ffmpeg'].zmq
        cmake.definitions['WITH_SDL2'] = self.options['ffmpeg'].sdl2
        cmake.definitions['WITH_X264'] = self.options['ffmpeg'].x264
        cmake.definitions['WITH_X265'] = self.options['ffmpeg'].x265
        cmake.definitions['WITH_VPX'] = self.options['ffmpeg'].vpx
        cmake.definitions['WITH_MP3LAME'] = self.options['ffmpeg'].mp3lame
        cmake.definitions['WITH_FDK_AAC'] = self.options['ffmpeg'].fdk_aac
        cmake.definitions['WITH_WEBP'] = self.options['ffmpeg'].webp
        cmake.definitions['WITH_OPENSSL'] = self.options['ffmpeg'].openssl

        if self.settings.os == "Linux":
            cmake.definitions['WITH_VAAPI'] = self.options['ffmpeg'].vaapi
            cmake.definitions['WITH_VDPAU'] = self.options['ffmpeg'].vdpau
            cmake.definitions['WITH_XCB'] = self.options['ffmpeg'].xcb
            cmake.definitions['WITH_ALSA'] = self.options['ffmpeg'].alsa
            cmake.definitions['WITH_PULSE'] = self.options['ffmpeg'].pulse

        if self.settings.os == "Macos":
            cmake.definitions['WITH_APPKIT'] = self.options['ffmpeg'].appkit
            cmake.definitions['WITH_AVFOUNDATION'] = self.options['ffmpeg'].avfoundation
            cmake.definitions['WITH_COREIMAGE'] = self.options['ffmpeg'].coreimage
            cmake.definitions['WITH_AUDIOTOOLBOX'] = self.options['ffmpeg'].audiotoolbox
            cmake.definitions['WITH_VIDEOTOOLBOX'] = self.options['ffmpeg'].videotoolbox
            cmake.definitions['WITH_SECURETRANSPORT'] = self.options['ffmpeg'].securetransport

        if self.settings.os == "Windows":
            cmake.definitions['WITH_QSV'] = self.options['ffmpeg'].qsv

        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        self.run(bin_path, run_environment=True)

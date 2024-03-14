from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.cmake import CMakeDeps
from conan.tools.files import copy
from conan.tools.build import cross_building

import os

class QtFfmpegTestConan(ConanFile):
    name = "qt_ffmpeg_test"
    settings    = "os", "compiler", "build_type", "arch"
    generators  = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def generate(self):
        conanlibs_path = os.path.join( self.build_folder, "thirdparty" )
        for dep in self.dependencies.values():
            for libdir in dep.cpp_info.libdirs:
                copy(self, "*.so", libdir, conanlibs_path )
                copy(self, "*.so.*", libdir, conanlibs_path )

    def requirements(self):
        self.requires( "qt/6.6.2" )
        self.requires( "intel-media-driver/23.4.3" )
        self.requires( "nlohmann_json/3.11.3" )
        self.requires( "spdlog/1.13.0" )

    def configure(self):
        self.options["qt"].shared=True
        self.options["qt"].opengl="desktop"
        self.options["qt"].openssl=True
        self.options["qt"].qtsvg=True
        self.options["qt"].qtdeclarative=True
        self.options["qt"].qt5compat=True
        self.options["qt"].qtcharts=False
        self.options["qt"].qtimageformats=False
        self.options["qt"].qtmultimedia=True
        self.options["qt"].qtlocation=False
        self.options["qt"].qtconnectivity=False
        self.options["qt"].with_ffmpeg=True
        self.options["qt"].with_pulseaudio=True

        self.options["ffmpeg"].shared=True
        self.options["ffmpeg"].fPIC=True
        self.options["ffmpeg"].avdevice=True
        self.options["ffmpeg"].avcodec=True
        self.options["ffmpeg"].avformat=True
        self.options["ffmpeg"].swresample=True
        self.options["ffmpeg"].swscale=True
        self.options["ffmpeg"].postproc=True
        self.options["ffmpeg"].avfilter=True
        self.options["ffmpeg"].with_asm=True
        self.options["ffmpeg"].with_bzip2=True
        self.options["ffmpeg"].with_lzma=True
        self.options["ffmpeg"].with_libiconv=True
        self.options["ffmpeg"].with_freetype=True
        self.options["ffmpeg"].with_openjpeg=True
        self.options["ffmpeg"].with_opus=True
        self.options["ffmpeg"].with_vorbis=True
        self.options["ffmpeg"].with_sdl=False
        self.options["ffmpeg"].with_libvpx=True
        self.options["ffmpeg"].with_libmp3lame=True
        self.options["ffmpeg"].with_libfdk_aac=True
        self.options["ffmpeg"].with_libwebp=True
        self.options["ffmpeg"].with_ssl="openssl"
        self.options["ffmpeg"].with_libalsa=True
        self.options["ffmpeg"].with_pulse=True
        self.options["ffmpeg"].with_vaapi=True
        self.options["ffmpeg"].with_vulkan=False
        self.options["ffmpeg"].with_xcb=True
        self.options["ffmpeg"].with_libdrm=True
        self.options["ffmpeg"].with_libsvtav1=True
        self.options["ffmpeg"].with_libaom=True
        self.options["ffmpeg"].with_libdav1d=True
        self.options["ffmpeg"].with_programs=False
        self.options["ffmpeg"].with_openh264=True
        self.options["ffmpeg"].with_libx264=False
        self.options["ffmpeg"].with_libx265=False
        self.options["ffmpeg"].with_cuvid=True
        self.options["ffmpeg"].with_libva=True
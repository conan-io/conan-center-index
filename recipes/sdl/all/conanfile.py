from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SDLConan(ConanFile):
    name = "sdl"
    description = "Access to audio, keyboard, mouse, joystick, and graphics hardware via OpenGL, Direct3D and Vulkan"
    topics = ("sdl2", "audio", "keyboard", "graphics", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = ["cmake", "pkg_config"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "directx": [True, False],
        "alsa": [True, False],
        "jack": [True, False],
        "pulse": [True, False],
        "sndio": [True, False],
        "nas": [True, False],
        "esd": [True, False],
        "arts": [True, False],
        "x11": [True, False],
        "xcursor": [True, False],
        "xinerama": [True, False],
        "xinput": [True, False],
        "xrandr": [True, False],
        "xscrnsaver": [True, False],
        "xshape": [True, False],
        "xvm": [True, False],
        "wayland": [True, False],
        "directfb": [True, False],
        "iconv": [True, False],
        "video_rpi": [True, False],
        "sdl2main": [True, False],
        "opengl": [True, False],
        "opengles": [True, False],
        "vulkan": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "directx": True,
        "alsa": True,
        "jack": True,
        "pulse": True,
        "sndio": False,
        "nas": True,
        "esd": False,
        "arts": False,
        "x11": True,
        "xcursor": True,
        "xinerama": True,
        "xinput": True,
        "xrandr": True,
        "xscrnsaver": True,
        "xshape": True,
        "xvm": True,
        "wayland": False,
        "directfb": False,
        "iconv": True,
        "video_rpi": False,
        "sdl2main": True,
        "opengl": True,
        "opengles": True,
        "vulkan": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if self.settings.compiler == "Visual Studio":
                del self.options.iconv
        if self.settings.os != "Linux":
            del self.options.alsa
            del self.options.jack
            del self.options.pulse
            del self.options.sndio
            del self.options.nas
            del self.options.esd
            del self.options.arts
            del self.options.x11
            del self.options.xcursor
            del self.options.xinerama
            del self.options.xinput
            del self.options.xrandr
            del self.options.xscrnsaver
            del self.options.xshape
            del self.options.xvm
            del self.options.wayland
            del self.options.directfb
            del self.options.video_rpi
        if self.settings.os != "Windows":
            del self.options.directx

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Macos" and not self.options.iconv:
            raise ConanInvalidConfiguration("On macOS iconv can't be disabled")
        if self.settings.os == "Linux":
            raise ConanInvalidConfiguration("Linux not supported yet")

    def requirements(self):
        if self.options.get_safe("iconv", False):
            self.requires("libiconv/1.16")
        if self.settings.os == "Linux":
            self.requires("xorg/system")
            if self.options.alsa:
                self.requires("libalsa/1.2.4")
            if self.options.pulse:
                self.requires("pulseaudio/13.0")
            if self.options.opengl:
                self.requires("opengl/system")

    def package_id(self):
        del self.info.options.sdl2main

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        # ensure sdl2-config is created for MinGW
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(NOT WINDOWS OR CYGWIN)",
                              "if(NOT WINDOWS OR CYGWIN OR MINGW)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(NOT (WINDOWS OR CYGWIN))",
                              "if(NOT (WINDOWS OR CYGWIN OR MINGW))")
        if self.version >= "2.0.14":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  'check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)',
                                  '# check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)')
        self._build_cmake()

    def _check_pkg_config(self, option, package_name):
        if option:
            pkg_config = tools.PkgConfig(package_name)
            if not pkg_config.provides:
                raise ConanInvalidConfiguration("package %s is not available" % package_name)

    def _check_dependencies(self):
        if self.settings.os == "Linux":
            self._check_pkg_config(self.options.jack, "jack")
            self._check_pkg_config(self.options.esd, "esound")
            self._check_pkg_config(self.options.wayland, "wayland-client")
            self._check_pkg_config(self.options.wayland, "wayland-protocols")
            self._check_pkg_config(self.options.directfb, "directfb")

    def validate(self):
        self._check_dependencies()

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            # FIXME: self.install_folder not defined? Neccessary?
            self._cmake.definitions["CONAN_INSTALL_FOLDER"] = self.install_folder
            if self.settings.os != "Windows":
                if not self.options.shared:
                    self._cmake.definitions["SDL_STATIC_PIC"] = self.options.fPIC
            if self.settings.compiler == "Visual Studio" and not self.options.shared:
                self._cmake.definitions["HAVE_LIBC"] = True
            self._cmake.definitions["SDL_SHARED"] = self.options.shared
            self._cmake.definitions["SDL_STATIC"] = not self.options.shared
            self._cmake.definitions["VIDEO_OPENGL"] = self.options.opengl
            self._cmake.definitions["VIDEO_OPENGLES"] = self.options.opengles
            self._cmake.definitions["VIDEO_VULKAN"] = self.options.vulkan
            if self.settings.os == "Linux":
                # See https://github.com/bincrafters/community/issues/696
                self._cmake.definitions["SDL_VIDEO_DRIVER_X11_SUPPORTS_GENERIC_EVENTS"] = 1

                self._cmake.definitions["ALSA"] = self.options.alsa
                if self.options.alsa:
                    self._cmake.definitions["HAVE_ASOUNDLIB_H"] = True
                    self._cmake.definitions["HAVE_LIBASOUND"] = True
                self._cmake.definitions["JACK"] = self.options.jack
                self._cmake.definitions["PULSEAUDIO"] = self.options.pulse
                self._cmake.definitions["SNDIO"] = self.options.sndio
                self._cmake.definitions["NAS"] = self.options.nas
                self._cmake.definitions["VIDEO_X11"] = self.options.x11
                if self.options.x11:
                    self._cmake.definitions["HAVE_XEXT_H"] = True
                self._cmake.definitions["VIDEO_X11_XCURSOR"] = self.options.xcursor
                if self.options.xcursor:
                    self._cmake.definitions["HAVE_XCURSOR_H"] = True
                self._cmake.definitions["VIDEO_X11_XINERAMA"] = self.options.xinerama
                if self.options.xinerama:
                    self._cmake.definitions["HAVE_XINERAMA_H"] = True
                self._cmake.definitions["VIDEO_X11_XINPUT"] = self.options.xinput
                if self.options.xinput:
                    self._cmake.definitions["HAVE_XINPUT_H"] = True
                self._cmake.definitions["VIDEO_X11_XRANDR"] = self.options.xrandr
                if self.options.xrandr:
                    self._cmake.definitions["HAVE_XRANDR_H"] = True
                self._cmake.definitions["VIDEO_X11_XSCRNSAVER"] = self.options.xscrnsaver
                if self.options.xscrnsaver:
                    self._cmake.definitions["HAVE_XSS_H"] = True
                self._cmake.definitions["VIDEO_X11_XSHAPE"] = self.options.xshape
                if self.options.xshape:
                    self._cmake.definitions["HAVE_XSHAPE_H"] = True
                self._cmake.definitions["VIDEO_X11_XVM"] = self.options.xvm
                if self.options.xvm:
                    self._cmake.definitions["HAVE_XF86VM_H"] = True
                self._cmake.definitions["VIDEO_WAYLAND"] = self.options.wayland
                self._cmake.definitions["VIDEO_DIRECTFB"] = self.options.directfb
                self._cmake.definitions["VIDEO_RPI"] = self.options.video_rpi
            elif self.settings.os == "Windows":
                self._cmake.definitions["DIRECTX"] = self.options.directx

            self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def _build_cmake(self):
        if self.settings.os == "Linux":
            if self.options.pulse:
                tools.rename("libpulse.pc", "libpulse-simple.pc")
        lib_paths = [lib for dep in self.deps_cpp_info.deps for lib in self.deps_cpp_info[dep].lib_paths]
        with tools.environment_append({"LIBRARY_PATH": os.pathsep.join(lib_paths)}):
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy(pattern="COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "sdl2-config")
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "libdata"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def _add_libraries_from_pc(self, library, static=None):
        if static is None:
            static = not self.options.shared
        pkg_config = tools.PkgConfig(library, static=static)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.components["libsdl2"].libs.extend(libs)
        self.cpp_info.components["libsdl2"].libdirs.extend(lib_paths)
        self.cpp_info.components["libsdl2"].sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.components["libsdl2"].exelinkflags.extend(pkg_config.libs_only_other)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SDL2"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2"

        postfix = "d" if self.settings.build_type == "Debug" else ""
        # SDL2
        sdl2_cmake_target = "SDL2" if self.options.shared else "SDL2-static"
        self.cpp_info.components["libsdl2"].names["cmake_find_package"] = sdl2_cmake_target
        self.cpp_info.components["libsdl2"].names["cmake_find_package_multi"] = sdl2_cmake_target
        self.cpp_info.components["libsdl2"].includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.components["libsdl2"].libs = ["SDL2" + postfix]
        if self.options.get_safe("iconv", False):
            self.cpp_info.components["libsdl2"].requires.append("libiconv::libiconv")
        if self.settings.os == "Linux":
            self.cpp_info.components["libsdl2"].system_libs = ["dl", "rt", "pthread"]
            self.cpp_info.components["libsdl2"].requires.append("xorg::xorg")
            if self.options.alsa:
                self.cpp_info.components["libsdl2"].requires.append("libalsa::libalsa")
            if self.options.pulse:
                self.cpp_info.components["libsdl2"].requires.append("pulseaudio::pulseaudio")
            if self.options.opengl:
                self.cpp_info.components["libsdl2"].requires.append("opengl::opengl")
            if self.options.jack:
                self._add_libraries_from_pc("jack")
            if self.options.sndio:
                self._add_libraries_from_pc("sndio")
            if self.options.nas:
                self.cpp_info.components["libsdl2"].libs.append("audio")
            if self.options.esd:
                self._add_libraries_from_pc("esound")
            if self.options.directfb:
                self._add_libraries_from_pc("directfb")
            if self.options.video_rpi:
                self.cpp_info.components["libsdl2"].libs.append("bcm_host")
                self.cpp_info.components["libsdl2"].includedirs.extend([
                    "/opt/vc/include",
                    "/opt/vc/include/interface/vcos/pthreads",
                    "/opt/vc/include/interface/vmcs_host/linux"
                ])
                self.cpp_info.components["libsdl2"].libdirs.append("/opt/vc/lib")
                self.cpp_info.components["libsdl2"].sharedlinkflags.append("-Wl,-rpath,/opt/vc/lib")
                self.cpp_info.components["libsdl2"].exelinkflags.append("-Wl,-rpath,/opt/vc/lib")
        elif self.settings.os == "Macos":
            self.cpp_info.components["libsdl2"].frameworks = ["Cocoa", "Carbon", "IOKit", "CoreVideo", "CoreAudio", "AudioToolbox", "ForceFeedback"]
            if tools.Version(self.version) >= "2.0.14":
                self.cpp_info.components["libsdl2"].frameworks.append("Metal")
        elif self.settings.os == "Windows":
            self.cpp_info.components["libsdl2"].system_libs = ["user32", "gdi32", "winmm", "imm32", "ole32", "oleaut32", "version", "uuid", "advapi32", "setupapi", "shell32"]
            if self.settings.compiler == "gcc":
                self.cpp_info.components["libsdl2"].system_libs.append("mingw32")
        # SDL2main
        if self.options.sdl2main:
            self.cpp_info.components["sdl2main"].names["cmake_find_package"] = "SDL2main"
            self.cpp_info.components["sdl2main"].names["cmake_find_package_multi"] = "SDL2main"
            self.cpp_info.components["sdl2main"].libs = ["SDL2main" + postfix]
            self.cpp_info.components["sdl2main"].requires = ["libsdl2"]

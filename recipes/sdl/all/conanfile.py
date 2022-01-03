from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class SDLConan(ConanFile):
    name = "sdl"
    description = "Access to audio, keyboard, mouse, joystick, and graphics hardware via OpenGL, Direct3D and Vulkan"
    topics = ("sdl2", "audio", "keyboard", "graphics", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org"
    license = "Zlib"

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
        "libunwind": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "directx": True,
        "alsa": True,
        "jack": False,
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
        "wayland": True,
        "directfb": False,
        "iconv": True,
        "video_rpi": False,
        "sdl2main": True,
        "opengl": True,
        "opengles": True,
        "vulkan": True,
        "libunwind": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = ["cmake", "pkg_config"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if self.settings.compiler in ["Visual Studio", "msvc"]:
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
            del self.options.libunwind
        if self.settings.os != "Windows":
            del self.options.directx

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.get_safe("iconv", False):
            self.requires("libiconv/1.16")
        if self.settings.os == "Linux":
            if self.options.alsa:
                self.requires("libalsa/1.2.4")
            if self.options.pulse:
                self.requires("pulseaudio/14.2")
            if self.options.sndio:
                raise ConanInvalidConfiguration("Package for 'sndio' is not available (yet)")
            if self.options.opengl:
                self.requires("opengl/system")
            if self.options.nas:
                self.requires("nas/1.9.4")
            if self.options.jack:
                raise ConanInvalidConfiguration("Package for 'jack' is not available (yet)")
            if self.options.esd:
                raise ConanInvalidConfiguration("Package for 'esd' is not available (yet)")
            if self.options.wayland:
                self.requires("wayland/1.19.0")
                self.requires("xkbcommon/1.3.0")
                self.requires("egl/system")
            if self.options.directfb:
                raise ConanInvalidConfiguration("Package for 'directfb' is not available (yet)")
            if self.options.libunwind:
                self.requires("libunwind/1.5.0")

    def validate(self):
        if self.settings.os == "Macos" and not self.options.iconv:
            raise ConanInvalidConfiguration("On macOS iconv can't be disabled")

        # SDL>=2.0.18 requires xcode 12 or higher because it uses CoreHaptics.
        if tools.Version(self.version) >= "2.0.18" and tools.is_apple_os(self.settings.os) and tools.Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration("{}/{} requires xcode 12 or higher".format(self.name, self.version))

    def package_id(self):
        del self.info.options.sdl2main

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("pkgconf/1.7.4")
        if self.options.get_safe("wayland", False):
            self.build_requires("wayland/1.19.0")  # Provides wayland-scanner

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                        'check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)',
                        '# check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)')
        self._build_cmake()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        cmake_required_includes = []  # List of directories used by CheckIncludeFile (https://cmake.org/cmake/help/latest/module/CheckIncludeFile.html)
        cmake_extra_ldflags = []
        # FIXME: self.install_folder not defined? Neccessary?
        self._cmake.definitions["CONAN_INSTALL_FOLDER"] = self.install_folder
        if self.settings.os != "Windows" and not self.options.shared:
            self._cmake.definitions["SDL_STATIC_PIC"] = self.options.fPIC
        if self.settings.compiler in ["Visual Studio", "msvc"] and not self.options.shared:
            self._cmake.definitions["HAVE_LIBC"] = True
        self._cmake.definitions["SDL_SHARED"] = self.options.shared
        self._cmake.definitions["SDL_STATIC"] = not self.options.shared

        if tools.Version(self.version) < "2.0.18":
            self._cmake.definitions["VIDEO_OPENGL"] = self.options.opengl
            self._cmake.definitions["VIDEO_OPENGLES"] = self.options.opengles
            self._cmake.definitions["VIDEO_VULKAN"] = self.options.vulkan
            if self.settings.os == "Linux":
                # See https://github.com/bincrafters/community/issues/696
                self._cmake.definitions["SDL_VIDEO_DRIVER_X11_SUPPORTS_GENERIC_EVENTS"] = 1

                self._cmake.definitions["ALSA"] = self.options.alsa
                if self.options.alsa:
                    self._cmake.definitions["ALSA_SHARED"] = self.deps_cpp_info["libalsa"].shared
                    self._cmake.definitions["HAVE_ASOUNDLIB_H"] = True
                    self._cmake.definitions["HAVE_LIBASOUND"] = True
                self._cmake.definitions["JACK"] = self.options.jack
                if self.options.jack:
                    self._cmake.definitions["JACK_SHARED"] = self.deps_cpp_info["jack"].shared
                self._cmake.definitions["ESD"] = self.options.esd
                if self.options.esd:
                    self._cmake.definitions["ESD_SHARED"] = self.deps_cpp_info["esd"].shared
                self._cmake.definitions["PULSEAUDIO"] = self.options.pulse
                if self.options.pulse:
                    self._cmake.definitions["PULSEAUDIO_SHARED"] = self.deps_cpp_info["pulseaudio"].shared
                self._cmake.definitions["SNDIO"] = self.options.sndio
                if self.options.sndio:
                    self._cmake.definitions["SNDIO_SHARED"] = self.deps_cpp_info["sndio"].shared
                self._cmake.definitions["NAS"] = self.options.nas
                if self.options.nas:
                    cmake_extra_ldflags += ["-lXau"]  # FIXME: SDL sources doesn't take into account transitive dependencies
                    cmake_required_includes += [os.path.join(self.deps_cpp_info["nas"].rootpath, str(it)) for it in self.deps_cpp_info["nas"].includedirs]
                    self._cmake.definitions["NAS_SHARED"] = self.options["nas"].shared
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
                if self.options.wayland:
                    # FIXME: Otherwise 2.0.16 links with system wayland (from egl/system requirement)
                    cmake_extra_ldflags += ["-L{}".format(os.path.join(self.deps_cpp_info["wayland"].rootpath, it)) for it in self.deps_cpp_info["wayland"].libdirs]
                    self._cmake.definitions["WAYLAND_SHARED"] = self.options["wayland"].shared
                    self._cmake.definitions["WAYLAND_SCANNER_1_15_FOUND"] = 1  # FIXME: Check actual build-requires version

                self._cmake.definitions["VIDEO_DIRECTFB"] = self.options.directfb
                self._cmake.definitions["VIDEO_RPI"] = self.options.video_rpi
                self._cmake.definitions["HAVE_LIBUNWIND_H"] = self.options.libunwind
            elif self.settings.os == "Windows":
                self._cmake.definitions["DIRECTX"] = self.options.directx
        else:
            self._cmake.definitions["SDL_OPENGL"] = self.options.opengl
            self._cmake.definitions["SDL_OPENGLES"] = self.options.opengles
            self._cmake.definitions["SDL_VULKAN"] = self.options.vulkan
            if self.settings.os == "Linux":
                # See https://github.com/bincrafters/community/issues/696
                self._cmake.definitions["SDL_VIDEO_DRIVER_X11_SUPPORTS_GENERIC_EVENTS"] = 1

                self._cmake.definitions["SDL_ALSA"] = self.options.alsa
                if self.options.alsa:
                    self._cmake.definitions["SDL_ALSA_SHARED"] = self.deps_cpp_info["libalsa"].shared
                    self._cmake.definitions["HAVE_ASOUNDLIB_H"] = True
                    self._cmake.definitions["HAVE_LIBASOUND"] = True
                self._cmake.definitions["SDL_JACK"] = self.options.jack
                if self.options.jack:
                    self._cmake.definitions["SDL_JACK_SHARED"] = self.deps_cpp_info["jack"].shared
                self._cmake.definitions["SDL_ESD"] = self.options.esd
                if self.options.esd:
                    self._cmake.definitions["SDL_ESD_SHARED"] = self.deps_cpp_info["esd"].shared
                self._cmake.definitions["SDL_PULSEAUDIO"] = self.options.pulse
                if self.options.pulse:
                    self._cmake.definitions["SDL_PULSEAUDIO_SHARED"] = self.deps_cpp_info["pulseaudio"].shared
                self._cmake.definitions["SDL_SNDIO"] = self.options.sndio
                if self.options.sndio:
                    self._cmake.definitions["SDL_SNDIO_SHARED"] = self.deps_cpp_info["sndio"].shared
                self._cmake.definitions["SDL_NAS"] = self.options.nas
                if self.options.nas:
                    cmake_extra_ldflags += ["-lXau"]  # FIXME: SDL sources doesn't take into account transitive dependencies
                    cmake_required_includes += [os.path.join(self.deps_cpp_info["nas"].rootpath, str(it)) for it in self.deps_cpp_info["nas"].includedirs]
                    self._cmake.definitions["SDL_NAS_SHARED"] = self.options["nas"].shared
                self._cmake.definitions["SDL_X11"] = self.options.x11
                if self.options.x11:
                    self._cmake.definitions["HAVE_XEXT_H"] = True
                self._cmake.definitions["SDL_X11_XCURSOR"] = self.options.xcursor
                if self.options.xcursor:
                    self._cmake.definitions["HAVE_XCURSOR_H"] = True
                self._cmake.definitions["SDL_X11_XINERAMA"] = self.options.xinerama
                if self.options.xinerama:
                    self._cmake.definitions["HAVE_XINERAMA_H"] = True
                self._cmake.definitions["SDL_X11_XINPUT"] = self.options.xinput
                if self.options.xinput:
                    self._cmake.definitions["HAVE_XINPUT_H"] = True
                self._cmake.definitions["SDL_X11_XRANDR"] = self.options.xrandr
                if self.options.xrandr:
                    self._cmake.definitions["HAVE_XRANDR_H"] = True
                self._cmake.definitions["SDL_X11_XSCRNSAVER"] = self.options.xscrnsaver
                if self.options.xscrnsaver:
                    self._cmake.definitions["HAVE_XSS_H"] = True
                self._cmake.definitions["SDL_X11_XSHAPE"] = self.options.xshape
                if self.options.xshape:
                    self._cmake.definitions["HAVE_XSHAPE_H"] = True
                self._cmake.definitions["SDL_X11_XVM"] = self.options.xvm
                if self.options.xvm:
                    self._cmake.definitions["HAVE_XF86VM_H"] = True
                self._cmake.definitions["SDL_WAYLAND"] = self.options.wayland
                if self.options.wayland:
                    # FIXME: Otherwise 2.0.16 links with system wayland (from egl/system requirement)
                    cmake_extra_ldflags += ["-L{}".format(os.path.join(self.deps_cpp_info["wayland"].rootpath, it)) for it in self.deps_cpp_info["wayland"].libdirs]
                    self._cmake.definitions["SDL_WAYLAND_SHARED"] = self.options["wayland"].shared
                    self._cmake.definitions["WAYLAND_SCANNER_1_15_FOUND"] = 1  # FIXME: Check actual build-requires version

                self._cmake.definitions["SDL_DIRECTFB"] = self.options.directfb
                self._cmake.definitions["SDL_RPI"] = self.options.video_rpi
                self._cmake.definitions["HAVE_LIBUNWIND_H"] = self.options.libunwind
            elif self.settings.os == "Windows":
                self._cmake.definitions["SDL_DIRECTX"] = self.options.directx

        # Add extra information collected from the deps
        self._cmake.definitions["EXTRA_LDFLAGS"] = " ".join(cmake_extra_ldflags)
        self._cmake.definitions["CMAKE_REQUIRED_INCLUDES"] = ";".join(cmake_required_includes)
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def _build_cmake(self):
        lib_paths = [lib for dep in self.deps_cpp_info.deps for lib in self.deps_cpp_info[dep].lib_paths]
        with tools.environment_append({"LIBRARY_PATH": os.pathsep.join(lib_paths)}):
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        if self.version >= "2.0.16":
            self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        else:
            self.copy(pattern="COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "sdl2-config")
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "libdata"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL2")

        self.cpp_info.names["cmake_find_package"] = "SDL2"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2"

        postfix = "d" if self.settings.build_type == "Debug" else ""

        # SDL2
        sdl2_cmake_target = "SDL2" if self.options.shared else "SDL2-static"
        self.cpp_info.components["libsdl2"].set_property("cmake_target_name", "SDL2::{}".format(sdl2_cmake_target))
        self.cpp_info.components["libsdl2"].set_property("pkg_config_name", "sdl2")

        self.cpp_info.components["libsdl2"].names["cmake_find_package"] = sdl2_cmake_target
        self.cpp_info.components["libsdl2"].names["cmake_find_package_multi"] = sdl2_cmake_target

        self.cpp_info.components["libsdl2"].includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.components["libsdl2"].libs = ["SDL2" + postfix]
        if self.options.get_safe("iconv", False):
            self.cpp_info.components["libsdl2"].requires.append("libiconv::libiconv")
        if self.settings.os == "Linux":
            self.cpp_info.components["libsdl2"].system_libs = ["dl", "rt", "pthread"]
            if self.options.alsa:
                self.cpp_info.components["libsdl2"].requires.append("libalsa::libalsa")
            if self.options.pulse:
                self.cpp_info.components["libsdl2"].requires.append("pulseaudio::pulseaudio")
            if self.options.opengl:
                self.cpp_info.components["libsdl2"].requires.append("opengl::opengl")
            if self.options.jack:
                self.cpp_info.components["libsdl2"].requires.append("jack::jack")
            if self.options.sndio:
                self.cpp_info.components["libsdl2"].requires.append("sndio::sndio")
            if self.options.nas:
                self.cpp_info.components["libsdl2"].requires.append("nas::nas")
            if self.options.esd:
                self.cpp_info.components["libsdl2"].requires.append("esd::esd")
            if self.options.directfb:
                self.cpp_info.components["libsdl2"].requires.append("directfb::directfb")
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
            if self.options.wayland:
                self.cpp_info.components["libsdl2"].requires.append("wayland::wayland")
                self.cpp_info.components["libsdl2"].requires.append("xkbcommon::xkbcommon")
                self.cpp_info.components["libsdl2"].requires.append("egl::egl")
            if self.options.libunwind:
                self.cpp_info.components["libsdl2"].requires.append("libunwind::libunwind")
        elif tools.is_apple_os(self.settings.os):
            self.cpp_info.components["libsdl2"].frameworks = [
                "CoreVideo", "CoreAudio", "AudioToolbox",
                "AVFoundation", "Foundation", "QuartzCore",
            ]
            if self.settings.os == "Macos":
                self.cpp_info.components["libsdl2"].frameworks.extend(["Cocoa", "Carbon", "IOKit", "ForceFeedback"])
                if tools.Version(self.version) >= "2.0.18":
                    self.cpp_info.components["libsdl2"].frameworks.append("GameController")
            elif self.settings.os in ["iOS", "tvOS", "watchOS"]:
                self.cpp_info.components["libsdl2"].frameworks.extend([
                    "UIKit", "OpenGLES", "GameController", "CoreMotion",
                    "CoreGraphics", "CoreBluetooth", "CoreHaptics",
                ])
            if tools.Version(self.version) >= "2.0.14":
                self.cpp_info.components["libsdl2"].frameworks.append("Metal")
            if tools.Version(self.version) >= "2.0.18":
                self.cpp_info.components["libsdl2"].frameworks.append("CoreHaptics")
        elif self.settings.os == "Windows":
            self.cpp_info.components["libsdl2"].system_libs = ["user32", "gdi32", "winmm", "imm32", "ole32", "oleaut32", "version", "uuid", "advapi32", "setupapi", "shell32"]
            if self.settings.compiler == "gcc":
                self.cpp_info.components["libsdl2"].system_libs.append("mingw32")

        # SDL2main
        if self.options.sdl2main:
            self.cpp_info.components["sdl2main"].set_property("cmake_target_name", "SDL2::SDL2main")

            self.cpp_info.components["sdl2main"].names["cmake_find_package"] = "SDL2main"
            self.cpp_info.components["sdl2main"].names["cmake_find_package_multi"] = "SDL2main"

            self.cpp_info.components["sdl2main"].libs = ["SDL2main" + postfix]
            self.cpp_info.components["sdl2main"].requires = ["libsdl2"]

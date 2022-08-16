from conan.tools.microsoft import is_msvc
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


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

    generators = ["cmake", "pkg_config"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if is_msvc(self):
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
            self.requires("libiconv/1.17")
        if self.settings.os == "Linux":
            if self.options.alsa:
                self.requires("libalsa/1.2.7.2")
            if self.options.pulse:
                self.requires("pulseaudio/14.2")
            if self.options.opengl:
                self.requires("opengl/system")
            if self.options.nas:
                self.requires("nas/1.9.4")
            if self.options.wayland:
                self.requires("wayland/1.20.0")
                self.requires("xkbcommon/1.4.1")
                self.requires("egl/system")
            if self.options.libunwind:
                self.requires("libunwind/1.6.2")

    def validate(self):
        if self.settings.os != "Macos": # REMOVE AFTER TEST
            raise ConanInvalidConfiguration("Excluded for reasons")

        if self.settings.os == "Macos" and not self.options.iconv:
            raise ConanInvalidConfiguration("On macOS iconv can't be disabled")

        # SDL>=2.0.18 requires xcode 12 or higher because it uses CoreHaptics.
        if tools.Version(self.version) >= "2.0.18" and tools.is_apple_os(self.settings.os) and tools.Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration("{}/{} requires xcode 12 or higher".format(self.name, self.version))

        if self.settings.os == "Linux":
            if self.options.sndio:
                raise ConanInvalidConfiguration("Package for 'sndio' is not available (yet)")
            if self.options.jack:
                raise ConanInvalidConfiguration("Package for 'jack' is not available (yet)")
            if self.options.esd:
                raise ConanInvalidConfiguration("Package for 'esd' is not available (yet)")
            if self.options.directfb:
                raise ConanInvalidConfiguration("Package for 'directfb' is not available (yet)")

    def package_id(self):
        if tools.Version(self.version) < "2.0.22":
            del self.info.options.sdl2main

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("pkgconf/1.7.4")
        if hasattr(self, "settings_build") and self.options.get_safe("wayland"):
            self.build_requires("wayland/1.20.0")  # Provides wayland-scanner

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                        'check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)',
                        '# check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)')

        # Ensure to find wayland-scanner from wayland recipe in build requirements (or requirements if 1 profile)
        if self.options.get_safe("wayland") and tools.Version(self.version) >= "2.0.18":
            wayland_bin_path = " ".join("\"{}\"".format(path) for path in self.deps_env_info["wayland"].PATH)
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "cmake", "sdlchecks.cmake"),
                "find_program(WAYLAND_SCANNER NAMES wayland-scanner REQUIRED)",
                "find_program(WAYLAND_SCANNER NAMES wayland-scanner REQUIRED PATHS {} NO_DEFAULT_PATH)".format(wayland_bin_path),
            )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if tools.is_apple_os(self) and self.settings.arch == "armv8":
            cmake.definitions["CMAKE_OBJC_FLAGS"] = "-arch arm64"
        cmake.verbose = True # REMOVE AFTER TEST
        cmake_required_includes = []  # List of directories used by CheckIncludeFile (https://cmake.org/cmake/help/latest/module/CheckIncludeFile.html)
        cmake_extra_ldflags = []
        # FIXME: self.install_folder not defined? Neccessary?
        cmake.definitions["CONAN_INSTALL_FOLDER"] = self.install_folder
        if self.settings.os != "Windows" and not self.options.shared:
            cmake.definitions["SDL_STATIC_PIC"] = self.options.fPIC
        if is_msvc(self) and not self.options.shared:
            cmake.definitions["HAVE_LIBC"] = True
        cmake.definitions["SDL_SHARED"] = self.options.shared
        cmake.definitions["SDL_STATIC"] = not self.options.shared

        if tools.Version(self.version) < "2.0.18":
            cmake.definitions["VIDEO_OPENGL"] = self.options.opengl
            cmake.definitions["VIDEO_OPENGLES"] = self.options.opengles
            cmake.definitions["VIDEO_VULKAN"] = self.options.vulkan
            if self.settings.os == "Linux":
                # See https://github.com/bincrafters/community/issues/696
                cmake.definitions["SDL_VIDEO_DRIVER_X11_SUPPORTS_GENERIC_EVENTS"] = 1

                cmake.definitions["ALSA"] = self.options.alsa
                if self.options.alsa:
                    cmake.definitions["ALSA_SHARED"] = self.deps_cpp_info["libalsa"].shared
                    cmake.definitions["HAVE_ASOUNDLIB_H"] = True
                    cmake.definitions["HAVE_LIBASOUND"] = True
                cmake.definitions["JACK"] = self.options.jack
                if self.options.jack:
                    cmake.definitions["JACK_SHARED"] = self.deps_cpp_info["jack"].shared
                cmake.definitions["ESD"] = self.options.esd
                if self.options.esd:
                    cmake.definitions["ESD_SHARED"] = self.deps_cpp_info["esd"].shared
                cmake.definitions["PULSEAUDIO"] = self.options.pulse
                if self.options.pulse:
                    cmake.definitions["PULSEAUDIO_SHARED"] = self.deps_cpp_info["pulseaudio"].shared
                cmake.definitions["SNDIO"] = self.options.sndio
                if self.options.sndio:
                    cmake.definitions["SNDIO_SHARED"] = self.deps_cpp_info["sndio"].shared
                cmake.definitions["NAS"] = self.options.nas
                if self.options.nas:
                    cmake_extra_ldflags += ["-lXau"]  # FIXME: SDL sources doesn't take into account transitive dependencies
                    cmake_required_includes += [os.path.join(self.deps_cpp_info["nas"].rootpath, str(it)) for it in self.deps_cpp_info["nas"].includedirs]
                    cmake.definitions["NAS_SHARED"] = self.options["nas"].shared
                cmake.definitions["VIDEO_X11"] = self.options.x11
                if self.options.x11:
                    cmake.definitions["HAVE_XEXT_H"] = True
                cmake.definitions["VIDEO_X11_XCURSOR"] = self.options.xcursor
                if self.options.xcursor:
                    cmake.definitions["HAVE_XCURSOR_H"] = True
                cmake.definitions["VIDEO_X11_XINERAMA"] = self.options.xinerama
                if self.options.xinerama:
                    cmake.definitions["HAVE_XINERAMA_H"] = True
                cmake.definitions["VIDEO_X11_XINPUT"] = self.options.xinput
                if self.options.xinput:
                    cmake.definitions["HAVE_XINPUT_H"] = True
                cmake.definitions["VIDEO_X11_XRANDR"] = self.options.xrandr
                if self.options.xrandr:
                    cmake.definitions["HAVE_XRANDR_H"] = True
                cmake.definitions["VIDEO_X11_XSCRNSAVER"] = self.options.xscrnsaver
                if self.options.xscrnsaver:
                    cmake.definitions["HAVE_XSS_H"] = True
                cmake.definitions["VIDEO_X11_XSHAPE"] = self.options.xshape
                if self.options.xshape:
                    cmake.definitions["HAVE_XSHAPE_H"] = True
                cmake.definitions["VIDEO_X11_XVM"] = self.options.xvm
                if self.options.xvm:
                    cmake.definitions["HAVE_XF86VM_H"] = True
                cmake.definitions["VIDEO_WAYLAND"] = self.options.wayland
                if self.options.wayland:
                    # FIXME: Otherwise 2.0.16 links with system wayland (from egl/system requirement)
                    cmake_extra_ldflags += ["-L{}".format(os.path.join(self.deps_cpp_info["wayland"].rootpath, it)) for it in self.deps_cpp_info["wayland"].libdirs]
                    cmake.definitions["WAYLAND_SHARED"] = self.options["wayland"].shared
                    cmake.definitions["WAYLAND_SCANNER_1_15_FOUND"] = 1  # FIXME: Check actual build-requires version

                cmake.definitions["VIDEO_DIRECTFB"] = self.options.directfb
                cmake.definitions["VIDEO_RPI"] = self.options.video_rpi
                cmake.definitions["HAVE_LIBUNWIND_H"] = self.options.libunwind
            elif self.settings.os == "Windows":
                cmake.definitions["DIRECTX"] = self.options.directx
        else:
            cmake.definitions["SDL_OPENGL"] = self.options.opengl
            cmake.definitions["SDL_OPENGLES"] = self.options.opengles
            cmake.definitions["SDL_VULKAN"] = self.options.vulkan
            if self.settings.os == "Linux":
                # See https://github.com/bincrafters/community/issues/696
                cmake.definitions["SDL_VIDEO_DRIVER_X11_SUPPORTS_GENERIC_EVENTS"] = 1

                cmake.definitions["SDL_ALSA"] = self.options.alsa
                if self.options.alsa:
                    cmake.definitions["SDL_ALSA_SHARED"] = self.deps_cpp_info["libalsa"].shared
                    cmake.definitions["HAVE_ASOUNDLIB_H"] = True
                    cmake.definitions["HAVE_LIBASOUND"] = True
                cmake.definitions["SDL_JACK"] = self.options.jack
                if self.options.jack:
                    cmake.definitions["SDL_JACK_SHARED"] = self.deps_cpp_info["jack"].shared
                cmake.definitions["SDL_ESD"] = self.options.esd
                if self.options.esd:
                    cmake.definitions["SDL_ESD_SHARED"] = self.deps_cpp_info["esd"].shared
                cmake.definitions["SDL_PULSEAUDIO"] = self.options.pulse
                if self.options.pulse:
                    cmake.definitions["SDL_PULSEAUDIO_SHARED"] = self.deps_cpp_info["pulseaudio"].shared
                cmake.definitions["SDL_SNDIO"] = self.options.sndio
                if self.options.sndio:
                    cmake.definitions["SDL_SNDIO_SHARED"] = self.deps_cpp_info["sndio"].shared
                cmake.definitions["SDL_NAS"] = self.options.nas
                if self.options.nas:
                    cmake_extra_ldflags += ["-lXau"]  # FIXME: SDL sources doesn't take into account transitive dependencies
                    cmake_required_includes += [os.path.join(self.deps_cpp_info["nas"].rootpath, str(it)) for it in self.deps_cpp_info["nas"].includedirs]
                    cmake.definitions["SDL_NAS_SHARED"] = self.options["nas"].shared
                cmake.definitions["SDL_X11"] = self.options.x11
                if self.options.x11:
                    cmake.definitions["HAVE_XEXT_H"] = True
                cmake.definitions["SDL_X11_XCURSOR"] = self.options.xcursor
                if self.options.xcursor:
                    cmake.definitions["HAVE_XCURSOR_H"] = True
                cmake.definitions["SDL_X11_XINERAMA"] = self.options.xinerama
                if self.options.xinerama:
                    cmake.definitions["HAVE_XINERAMA_H"] = True
                cmake.definitions["SDL_X11_XINPUT"] = self.options.xinput
                if self.options.xinput:
                    cmake.definitions["HAVE_XINPUT_H"] = True
                cmake.definitions["SDL_X11_XRANDR"] = self.options.xrandr
                if self.options.xrandr:
                    cmake.definitions["HAVE_XRANDR_H"] = True
                cmake.definitions["SDL_X11_XSCRNSAVER"] = self.options.xscrnsaver
                if self.options.xscrnsaver:
                    cmake.definitions["HAVE_XSS_H"] = True
                cmake.definitions["SDL_X11_XSHAPE"] = self.options.xshape
                if self.options.xshape:
                    cmake.definitions["HAVE_XSHAPE_H"] = True
                cmake.definitions["SDL_X11_XVM"] = self.options.xvm
                if self.options.xvm:
                    cmake.definitions["HAVE_XF86VM_H"] = True
                cmake.definitions["SDL_WAYLAND"] = self.options.wayland
                if self.options.wayland:
                    # FIXME: Otherwise 2.0.16 links with system wayland (from egl/system requirement)
                    cmake_extra_ldflags += ["-L{}".format(os.path.join(self.deps_cpp_info["wayland"].rootpath, it)) for it in self.deps_cpp_info["wayland"].libdirs]
                    cmake.definitions["SDL_WAYLAND_SHARED"] = self.options["wayland"].shared

                cmake.definitions["SDL_DIRECTFB"] = self.options.directfb
                cmake.definitions["SDL_RPI"] = self.options.video_rpi
                cmake.definitions["HAVE_LIBUNWIND_H"] = self.options.libunwind
            elif self.settings.os == "Windows":
                cmake.definitions["SDL_DIRECTX"] = self.options.directx

        if tools.Version(self.version) >= "2.0.22":
            cmake.definitions["SDL2_DISABLE_SDL2MAIN"] = not self.options.sdl2main

        # Add extra information collected from the deps
        cmake.definitions["EXTRA_LDFLAGS"] = " ".join(cmake_extra_ldflags)
        cmake.definitions["CMAKE_REQUIRED_INCLUDES"] = ";".join(cmake_required_includes)
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
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

        postfix = "d" if self.settings.os != "Android" and self.settings.build_type == "Debug" else ""

        # SDL2
        self.cpp_info.components["libsdl2"].set_property("cmake_target_name", "SDL2::SDL2")
        if not self.options.shared:
            self.cpp_info.components["libsdl2"].set_property("cmake_target_aliases", ["SDL2::SDL2-static"])
        self.cpp_info.components["libsdl2"].set_property("pkg_config_name", "sdl2")

        sdl2_cmake_target = "SDL2" if self.options.shared else "SDL2-static"
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

        # Workaround to avoid unwanted sdl::sdl target in CMakeDeps generator
        self.cpp_info.set_property(
            "cmake_target_name",
            "SDL2::{}".format("SDL2main" if self.options.sdl2main else "SDL2"),
        )

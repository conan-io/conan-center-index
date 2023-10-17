from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class SDLConan(ConanFile):
    name = "sdl"
    description = "Access to audio, keyboard, mouse, joystick, and graphics hardware via OpenGL, Direct3D and Vulkan"
    topics = ("sdl2", "audio", "keyboard", "graphics", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org"
    license = "Zlib"
    package_type = "library"
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
        "nas": False,
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
        "video_rpi": False,
        "sdl2main": True,
        "opengl": True,
        "opengles": True,
        "vulkan": True,
        "libunwind": True,
    }

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang" and \
               self.settings.compiler.get_safe("runtime")

    def config_options(self):
        # Don't depend on iconv on macOS by default
        # SDL2 depends on many system freamworks,
        # which depend on the system-provided iconv
        # and can conflict with the Conan provided one
        self.options.iconv = self.settings.os != "Macos"

        if self.settings.os == "Windows":
            del self.options.fPIC
            if (is_msvc(self) or self._is_clang_cl):
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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("iconv", False):
            self.requires("libiconv/1.17")
        if self.settings.os == "Linux":
            if self.options.alsa:
                self.requires("libalsa/1.2.10")
            if self.options.pulse:
                self.requires("pulseaudio/14.2")
            if self.options.opengl:
                self.requires("opengl/system")
            if self.options.nas:
                self.requires("nas/1.9.5")
            if self.options.wayland:
                self.requires("wayland/1.22.0")
                self.requires("xkbcommon/1.6.0")
                self.requires("egl/system")
            if self.options.libunwind:
                self.requires("libunwind/1.7.2")

    def validate(self):
        # SDL>=2.0.18 requires xcode 12 or higher because it uses CoreHaptics.
        if is_apple_os(self) and Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration(f"{self.ref} requires xcode 12 or higher")

        if self.settings.os == "Linux":
            if self.options.sndio:
                raise ConanInvalidConfiguration("Package for 'sndio' is not available (yet)")
            if self.options.jack:
                raise ConanInvalidConfiguration("Package for 'jack' is not available (yet)")
            if self.options.esd:
                raise ConanInvalidConfiguration("Package for 'esd' is not available (yet)")
            if self.options.directfb:
                raise ConanInvalidConfiguration("Package for 'directfb' is not available (yet)")

    def build_requirements(self):
        if self.settings.os == "Macos" and cross_building(self):
            # Workaround for CMake bug with error message:
            # Attempting to use @rpath without CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being
            # set. This could be because you are using a Mac OS X version less than 10.5
            # or because CMake's platform configuration is corrupt.
            self.tool_requires("cmake/[>=3.20 <4]")
        if self.settings.os == "Linux" and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self.options.get_safe("wayland") and not self._is_legacy_one_profile:
            self.tool_requires("wayland/<host_version>")  # Provides wayland-scanner

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        if self.settings.os == "Linux" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < 5.0:
            tc.preprocessor_definitions["GBM_BO_USE_CURSOR"] = 2

        tc.variables["SDL2_DISABLE_INSTALL"] = False  # SDL2_* options will get renamed to SDL_ options in the next SDL release
        if is_apple_os(self):
            tc.variables["CMAKE_OSX_ARCHITECTURES"] = {
                "armv8": "arm64",
            }.get(str(self.settings.arch), str(self.settings.arch))

        if self.settings.os != "Windows" and not self.options.shared:
            tc.variables["SDL_STATIC_PIC"] = self.options.fPIC
        if (is_msvc(self) or self._is_clang_cl) and not self.options.shared:
            tc.variables["HAVE_LIBC"] = True
        tc.variables["SDL_SHARED"] = self.options.shared
        tc.variables["SDL_STATIC"] = not self.options.shared
        tc.variables["SDL_OPENGL"] = self.options.opengl
        tc.variables["SDL_OPENGLES"] = self.options.opengles
        tc.variables["SDL_VULKAN"] = self.options.vulkan
        if self.settings.os == "Linux":
            # See https://github.com/bincrafters/community/issues/696
            tc.variables["SDL_VIDEO_DRIVER_X11_SUPPORTS_GENERIC_EVENTS"] = 1

            tc.variables["SDL_ALSA"] = self.options.alsa
            if self.options.alsa:
                tc.variables["SDL_ALSA_SHARED"] = self.dependencies["libalsa"].options.shared
                tc.variables["HAVE_ASOUNDLIB_H"] = True
                tc.variables["HAVE_LIBASOUND"] = True
            tc.variables["SDL_JACK"] = self.options.jack
            if self.options.jack:
                tc.variables["SDL_JACK_SHARED"] = self.dependencies["jack"].options.shared
            tc.variables["SDL_ESD"] = self.options.esd
            if self.options.esd:
                tc.variables["SDL_ESD_SHARED"] = self.dependencies["esd"].options.shared
            tc.variables["SDL_PULSEAUDIO"] = self.options.pulse
            if self.options.pulse:
                tc.variables["SDL_PULSEAUDIO_SHARED"] = self.dependencies["pulseaudio"].options.shared
            tc.variables["SDL_SNDIO"] = self.options.sndio
            if self.options.sndio:
                tc.variables["SDL_SNDIO_SHARED"] = self.dependencies["sndio"].options.shared
            tc.variables["SDL_NAS"] = self.options.nas
            if self.options.nas:
                tc.variables["SDL_NAS_SHARED"] = self.dependencies["nas"].options.shared
            tc.variables["SDL_X11"] = self.options.x11
            if self.options.x11:
                tc.variables["HAVE_XEXT_H"] = True
            tc.variables["SDL_X11_XCURSOR"] = self.options.xcursor
            if self.options.xcursor:
                tc.variables["HAVE_XCURSOR_H"] = True
            tc.variables["SDL_X11_XINERAMA"] = self.options.xinerama
            if self.options.xinerama:
                tc.variables["HAVE_XINERAMA_H"] = True
            tc.variables["SDL_X11_XINPUT"] = self.options.xinput
            if self.options.xinput:
                tc.variables["HAVE_XINPUT_H"] = True
            tc.variables["SDL_X11_XRANDR"] = self.options.xrandr
            if self.options.xrandr:
                tc.variables["HAVE_XRANDR_H"] = True
            tc.variables["SDL_X11_XSCRNSAVER"] = self.options.xscrnsaver
            if self.options.xscrnsaver:
                tc.variables["HAVE_XSS_H"] = True
            tc.variables["SDL_X11_XSHAPE"] = self.options.xshape
            if self.options.xshape:
                tc.variables["HAVE_XSHAPE_H"] = True
            tc.variables["SDL_X11_XVM"] = self.options.xvm
            if self.options.xvm:
                tc.variables["HAVE_XF86VM_H"] = True
            tc.variables["SDL_WAYLAND"] = self.options.wayland
            if self.options.wayland:
                # FIXME: Otherwise 2.0.16 links with system wayland (from egl/system requirement)
                wayland_host = self.dependencies["wayland"] if self._is_legacy_one_profile else self.dependencies.host["wayland"]
                tc.variables["SDL_WAYLAND_SHARED"] = wayland_host.options.shared

                wayland_build = self.dependencies["wayland"] if self._is_legacy_one_profile else self.dependencies.build["wayland"]
                wayland_bin_dir = wayland_build.cpp_info.aggregated_components().bindirs[0] # for wayland scanner
                tc.variables["WAYLAND_BIN_DIR"] = wayland_bin_dir

            tc.variables["SDL_DIRECTFB"] = self.options.directfb
            tc.variables["SDL_RPI"] = self.options.video_rpi
            tc.variables["HAVE_LIBUNWIND_H"] = self.options.libunwind
        elif self.settings.os == "Windows":
            tc.variables["SDL_DIRECTX"] = self.options.directx

        tc.variables["SDL2_DISABLE_SDL2MAIN"] = not self.options.sdl2main

        # Add extra information collected from the deps
        all_deps = [dep for dep in reversed(self.dependencies.host.topological_sort.values())]
        if not is_msvc(self):
            deps_includes = [p for dep in all_deps for p in dep.cpp_info.aggregated_components().includedirs]
            tc.variables["CMAKE_REQUIRED_INCLUDES"] = ";".join(deps_includes)
            extra_cflags = [f"-I{p}" for p in deps_includes]
            extra_cflags += [f"-D{define}" for dep in all_deps for define in dep.cpp_info.aggregated_components().defines]
            tc.variables["EXTRA_CFLAGS"] = ";".join(extra_cflags)
            extra_ldflags = [f"-L{p}" for dep in all_deps for p in dep.cpp_info.aggregated_components().libdirs]
            tc.variables["EXTRA_LDFLAGS"] = ";".join(extra_ldflags)
            extra_libs = [lib for dep in all_deps for lib in dep.cpp_info.aggregated_components().libs]
            extra_libs += [lib for dep in all_deps for lib in dep.cpp_info.aggregated_components().system_libs]
            tc.variables["EXTRA_LIBS"] = ";".join(extra_libs)

        tc.generate()

        CMakeDeps(self).generate()
        PkgConfigDeps(self).generate()

        env = Environment()
        lib_paths = [lib for dep in all_deps for lib in dep.cpp_info.aggregated_components().libdirs]
        env.define_path("LIBRARY_PATH", os.pathsep.join(lib_paths))
        env.vars(self).save_script("sdl_library_path")

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        if self.settings.os == "Macos":
            if self.options.iconv:
                # If using conan-provided iconv, search for the symbol "libiconv_open"
                replace_check = "check_library_exists(iconv libiconv_open"
            else:
                # When no tusing conan-provided icon, don't check for iconv at all
                replace_check = "#check_library_exists(iconv iconv_open"
            replace_in_file(self, cmakelists, "check_library_exists(iconv iconv_open",
                            replace_check)

        # Avoid assuming iconv is available if it is provided by the C runtime,
        # and let SDL build the fallback implementation
        replace_in_file(self, cmakelists,
                        'check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)',
                        '# check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)')

        # Ensure to find wayland-scanner from wayland recipe in build requirements (or requirements if 1 profile)
        if self.options.get_safe("wayland"):
            replace_in_file(self,
                os.path.join(self.source_folder, "cmake", "sdlchecks.cmake"),
                "find_program(WAYLAND_SCANNER NAMES wayland-scanner REQUIRED)",
                'find_program(WAYLAND_SCANNER NAMES wayland-scanner REQUIRED PATHS "${WAYLAND_BIN_DIR}" NO_DEFAULT_PATH)',
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="LICENSE.txt", src=os.path.join(self.source_folder), dst=os.path.join(self.package_folder, "licenses"))
        rm(self, "sdl2-config", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "libdata"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL2")

        self.cpp_info.names["cmake_find_package"] = "SDL2"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2"

        postfix = "d" if self.settings.os != "Android" and self.settings.build_type == "Debug" else ""

        # SDL2
        if (is_msvc(self) or self._is_clang_cl) and not self.options.shared:
            lib_postfix = f"-static{postfix}"
        else:
            lib_postfix = postfix

        self.cpp_info.components["libsdl2"].set_property("cmake_target_name", "SDL2::SDL2")
        if not self.options.shared:
            self.cpp_info.components["libsdl2"].set_property("cmake_target_aliases", ["SDL2::SDL2-static"])
        self.cpp_info.components["libsdl2"].set_property("pkg_config_name", "sdl2")

        sdl2_cmake_target = "SDL2" if self.options.shared else "SDL2-static"
        self.cpp_info.components["libsdl2"].names["cmake_find_package"] = sdl2_cmake_target
        self.cpp_info.components["libsdl2"].names["cmake_find_package_multi"] = sdl2_cmake_target

        self.cpp_info.components["libsdl2"].includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.components["libsdl2"].libs = ["SDL2" + lib_postfix]
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
        elif is_apple_os(self) and not self.options.shared:
            self.cpp_info.components["libsdl2"].frameworks = [
                "CoreVideo", "CoreAudio", "AudioToolbox",
                "AVFoundation", "Foundation", "QuartzCore",
            ]
            if self.settings.os == "Macos":
                self.cpp_info.components["libsdl2"].frameworks.extend(["Cocoa", "Carbon", "IOKit", "ForceFeedback"])
                self.cpp_info.components["libsdl2"].frameworks.append("GameController")
            elif self.settings.os in ["iOS", "tvOS", "watchOS"]:
                self.cpp_info.components["libsdl2"].frameworks.extend([
                    "UIKit", "OpenGLES", "GameController", "CoreMotion",
                    "CoreGraphics", "CoreBluetooth",
                ])

            self.cpp_info.components["libsdl2"].frameworks.append("Metal")
            self.cpp_info.components["libsdl2"].sharedlinkflags.append("-Wl,-weak_framework,CoreHaptics")
            self.cpp_info.components["libsdl2"].exelinkflags.append("-Wl,-weak_framework,CoreHaptics")
        elif self.settings.os == "Windows":
            self.cpp_info.components["libsdl2"].system_libs = ["user32", "gdi32", "winmm", "imm32", "ole32", "oleaut32", "version", "uuid", "advapi32", "setupapi", "shell32"]
            if self.settings.compiler == "gcc":
                self.cpp_info.components["libsdl2"].system_libs.append("mingw32")
        elif self.settings.os == "Android" and not self.options.shared:
            self.cpp_info.components["libsdl2"].system_libs.extend(["android", "dl", "log"])
            if self.options.opengles:
                self.cpp_info.components["libsdl2"].system_libs.extend(["GLESv1_CM", "GLESv2"])
                self.cpp_info.components["libsdl2"].system_libs.append("OpenSLES")

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

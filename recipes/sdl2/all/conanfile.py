from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class SDL2Conan(ConanFile):
    name = "sdl2"
    description = "Access to audio, keyboard, mouse, joystick, and graphics hardware via OpenGL and Direct3D"
    topics = ("conan", "sdl2", "audio", "keyboard", "graphics", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt", "cmake.patch", "SDL_string.patch"]
    generators = ['cmake']
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "directx": [True, False],
        "alsa": [True, False],
        "jack": [True, False],
        "pulse": [True, False],
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
        "sdl2main": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "directx": True,
        "alsa": True,
        "jack": True,
        "pulse": True,
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
        "iconv": False,
        "video_rpi": False,
        "sdl2main": True
    }

    def requirements(self):
        if self.options.iconv:
            self.requires.add("libiconv/1.15")

    def system_requirements(self):
        if self.settings.os == "Linux" and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                if self.settings.arch == "x86":
                    arch_suffix = ':i386'
                elif self.settings.arch == "x86_64":
                    arch_suffix = ':amd64'
                elif self.settings.arch == "armv7":
                    arch_suffix = ':armhf'
                elif self.settings.arch == "armv8":
                    arch_suffix = ':arm64'
                packages = ['pkg-config%s' % arch_suffix]
                packages.append('mesa-common-dev%s' % arch_suffix)
                packages.append('libegl1-mesa-dev%s' % arch_suffix)
                packages.append('libgbm-dev%s' % arch_suffix)
                packages.append('libdrm-dev%s' % arch_suffix)
                if self.options.alsa:
                    packages.append('libasound2-dev%s' % arch_suffix)
                if self.options.jack:
                    packages.append('libjack-dev%s' % arch_suffix)
                if self.options.pulse:
                    packages.append('libpulse-dev%s' % arch_suffix)
                if self.options.nas:
                    packages.append('libaudio-dev%s' % arch_suffix)
                if self.options.esd:
                    packages.append('libesd0-dev%s' % arch_suffix)
                if self.options.arts:
                    packages.append('artsc0-dev%s' % arch_suffix)
                if self.options.x11:
                    packages.extend(['libx11-dev%s' % arch_suffix,
                                     'libxext-dev%s' % arch_suffix])
                if self.options.xcursor:
                    packages.append('libxcursor-dev%s' % arch_suffix)
                if self.options.xinerama:
                    packages.append('libxinerama-dev%s' % arch_suffix)
                if self.options.xinput:
                    packages.append('libxi-dev%s' % arch_suffix)
                if self.options.xrandr:
                    packages.append('libxrandr-dev%s' % arch_suffix)
                if self.options.xscrnsaver:
                    packages.append('libxss-dev%s' % arch_suffix)
                if self.options.xvm:
                    packages.append('libxxf86vm-dev%s' % arch_suffix)
                if self.options.wayland:
                    packages.extend(['libwayland-dev%s' % arch_suffix,
                                     'libxkbcommon-dev%s' % arch_suffix,
                                     'wayland-protocols'])
                if self.options.directfb:
                    packages.append('libdirectfb-dev%s' % arch_suffix)
                for package in packages:
                    installer.install(package)
            if tools.os_info.with_yum:
                installer = tools.SystemPackageTool()
                if self.settings.arch == "x86":
                    arch_suffix = '.i686'
                elif self.settings.arch == 'x86_64':
                    arch_suffix = '.x86_64'
                packages = ['mesa-libGL-devel%s' % arch_suffix,
                            'mesa-libEGL-devel%s' % arch_suffix,
                            'gdm-devel%s' % arch_suffix,
                            'libdrm-devel%s' % arch_suffix]
                if tools.os_info.linux_distro == 'centos':
                    packages.append('pkgconfig%s' % arch_suffix)
                elif tools.os_info.linux_distro == 'fedora':
                    packages.append('pkgconf-pkg-config%s' % arch_suffix)
                if self.options.alsa:
                    packages.append('alsa-lib-devel%s' % arch_suffix)
                if self.options.jack:
                    packages.append('jack-audio-connection-kit-devel%s' % arch_suffix)
                if self.options.pulse:
                    packages.append('pulseaudio-libs-devel%s' % arch_suffix)
                if self.options.nas:
                    packages.append('nas-devel%s' % arch_suffix)
                if self.options.esd:
                    packages.append('esound-devel%s' % arch_suffix)
                if self.options.x11:
                    packages.extend(['libX11-devel%s' % arch_suffix,
                                    'libXext-devel%s' % arch_suffix])
                if self.options.xcursor:
                    packages.append('libXcursor-devel%s' % arch_suffix)
                if self.options.xinerama:
                    packages.append('libXinerama-devel%s' % arch_suffix)
                if self.options.xinput:
                    packages.append('libXi-devel%s' % arch_suffix)
                if self.options.xrandr:
                    packages.append('libXrandr-devel%s' % arch_suffix)
                if self.options.xscrnsaver:
                    packages.append('libXScrnSaver-devel%s' % arch_suffix)
                if self.options.xvm:
                    packages.append('libXxf86vm-devel%s' % arch_suffix)
                if self.options.wayland:
                    packages.extend(['wayland-devel%s' % arch_suffix,
                                    'libxkbcommon-devel%s' % arch_suffix,
                                    'wayland-protocols-devel'])
                for package in packages:
                    installer.install(package)

    def config_options(self):
        if self.settings.os != "Linux":
            self.options.remove("alsa")
            self.options.remove("jack")
            self.options.remove("pulse")
            self.options.remove("nas")
            self.options.remove("esd")
            self.options.remove("arts")
            self.options.remove("x11")
            self.options.remove("xcursor")
            self.options.remove("xinerama")
            self.options.remove("xinput")
            self.options.remove("xrandr")
            self.options.remove("xscrnsaver")
            self.options.remove("xshape")
            self.options.remove("xvm")
            self.options.remove('wayland')
            self.options.remove('directfb')
            self.options.remove('video_rpi')
        if self.settings.os != "Windows":
            self.options.remove("directx")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SDL2-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)
        # Workaround for linker error with VS2019, see https://bugzilla.libsdl.org/show_bug.cgi?id=4759
        if self.settings.compiler == 'Visual Studio' and self.settings.compiler.version == 16:
            tools.patch(base_path=self._source_subfolder, patch_file="SDL_string.patch")

    def build(self):
        # ensure sdl2-config is created for MinGW
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(NOT WINDOWS OR CYGWIN)",
                              "if(NOT WINDOWS OR CYGWIN OR MINGW)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(NOT (WINDOWS OR CYGWIN))",
                              "if(NOT WINDOWS OR CYGWIN OR MINGW)")
        self.build_cmake()

    def check_pkg_config(self, option, package_name):
        if option:
            pkg_config = tools.PkgConfig(package_name)
            if not pkg_config.provides:
                raise ConanInvalidConfiguration('package %s is not available' % package_name)

    def check_dependencies(self):
        if self.settings.os == 'Linux':
            self.check_pkg_config(True, 'egl')
            self.check_pkg_config(True, 'libdrm')
            self.check_pkg_config(self.options.alsa, 'alsa')
            self.check_pkg_config(self.options.jack, 'jack')
            self.check_pkg_config(self.options.pulse, 'libpulse')
            self.check_pkg_config(self.options.esd, 'esound')
            self.check_pkg_config(self.options.x11, 'x11')
            self.check_pkg_config(self.options.x11, 'xext')
            self.check_pkg_config(self.options.xcursor, 'xcursor')
            self.check_pkg_config(self.options.xinerama, 'xinerama')
            self.check_pkg_config(self.options.xinput, 'xi')
            self.check_pkg_config(self.options.xrandr, 'xrandr')
            self.check_pkg_config(self.options.xscrnsaver, 'xscrnsaver')
            self.check_pkg_config(self.options.xvm, 'xxf86vm')
            self.check_pkg_config(self.options.wayland, 'wayland-client')
            self.check_pkg_config(self.options.wayland, 'xkbcommon')
            self.check_pkg_config(self.options.wayland, 'wayland-protocols')
            self.check_pkg_config(self.options.directfb, 'directfb')

    def _configure_cmake(self):
        self.check_dependencies()

        cmake = CMake(self)
        # FIXME: self.install_folder not defined? Neccessary?
        cmake.definitions['CONAN_INSTALL_FOLDER'] = self.install_folder
        if self.settings.os != 'Windows':
            if not self.options.shared:
                cmake.definitions['SDL_STATIC_PIC'] = self.options.fPIC
        if self.settings.compiler == 'Visual Studio' and not self.options.shared:
            cmake.definitions['HAVE_LIBC'] = True
        cmake.definitions['SDL_SHARED'] = self.options.shared
        cmake.definitions['SDL_STATIC'] = not self.options.shared
        if self.settings.os == "Linux":
            cmake.definitions['ALSA'] = self.options.alsa
            cmake.definitions['JACK'] = self.options.jack
            cmake.definitions['PULSEAUDIO'] = self.options.pulse
            cmake.definitions['NAS'] = self.options.nas
            cmake.definitions['VIDEO_X11'] = self.options.x11
            cmake.definitions['VIDEO_X11_XCURSOR'] = self.options.xcursor
            cmake.definitions['VIDEO_X11_XINERAMA'] = self.options.xinerama
            cmake.definitions['VIDEO_X11_XINPUT'] = self.options.xinput
            cmake.definitions['VIDEO_X11_XRANDR'] = self.options.xrandr
            cmake.definitions['VIDEO_X11_XSCRNSAVER'] = self.options.xscrnsaver
            cmake.definitions['VIDEO_X11_XSHAPE'] = self.options.xshape
            cmake.definitions['VIDEO_X11_XVM'] = self.options.xvm
            cmake.definitions['VIDEO_WAYLAND'] = self.options.wayland
            cmake.definitions['VIDEO_DIRECTFB'] = self.options.directfb
            cmake.definitions['VIDEO_RPI'] = self.options.video_rpi
        elif self.settings.os == "Windows":
            cmake.definitions["DIRECTX"] = self.options.directx

        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build_cmake(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install(build_dir=self._build_subfolder)
        self.copy(pattern="COPYING.txt", dst="license", src=self._source_subfolder)
        if self.settings.compiler == 'Visual Studio':
            self.copy(pattern="*.pdb", dst="lib", src=".")
        os.rename(os.path.join(self.package_folder, "license"), os.path.join(self.package_folder, "licenses"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", self._build_subfolder))

    def add_libraries_from_pc(self, library, static=None):
        if static is None:
            static = not self.options.shared
        pkg_config = tools.PkgConfig(library, static=static)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_paths)
        self.cpp_info.sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.exelinkflags.extend(pkg_config.libs_only_other)

    def package_id(self):
        del self.info.options.sdl2main

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        sdl2_config = os.path.join(self.package_folder, 'bin', "sdl2-config")
        self._chmod_plus_x(sdl2_config)
        self.output.info('Creating SDL2_CONFIG environment variable: %s' % sdl2_config)
        self.env_info.SDL2_CONFIG = sdl2_config
        self.output.info('Creating SDL_CONFIG environment variable: %s' % sdl2_config)
        self.env_info.SDL_CONFIG = sdl2_config
        self.cpp_info.libs = [lib for lib in tools.collect_libs(self) if '2.0' not in lib]
        if not self.options.sdl2main:
            self.cpp_info.libs = [lib for lib in self.cpp_info.libs if 'main' not in lib]
        self.cpp_info.includedirs.append(os.path.join('include', 'SDL2'))
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(['dl', 'rt', 'pthread'])
            if self.options.alsa:
                self.add_libraries_from_pc('alsa')
            if self.options.jack:
                self.add_libraries_from_pc('jack')
            if self.options.pulse:
                self.add_libraries_from_pc('libpulse', False)
            if self.options.nas:
                self.cpp_info.libs.append('audio')
            if self.options.esd:
                self.add_libraries_from_pc('esound')
            if self.options.directfb:
                self.add_libraries_from_pc('directfb')
            if self.options.video_rpi:
                self.cpp_info.libs.append('bcm_host')
                self.cpp_info.includedirs.extend(["/opt/vc/include",
                                                  "/opt/vc/include/interface/vcos/pthreads",
                                                  "/opt/vc/include/interface/vmcs_host/linux"])
                self.cpp_info.libdirs.append("/opt/vc/lib")
                self.cpp_info.sharedlinkflags.append("-Wl,-rpath,/opt/vc/lib")
                self.cpp_info.exelinkflags.append("-Wl,-rpath,/opt/vc/lib")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(['Cocoa', 'Carbon', 'IOKit', 'CoreVideo', 'CoreAudio', 'AudioToolbox', 'ForceFeedback'])
            if not self.options.iconv:
                self.cpp_info.libs.append('iconv')
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(['user32', 'gdi32', 'winmm', 'imm32', 'ole32', 'oleaut32', 'version', 'uuid', 'advapi32', 'setupapi', 'shell32'])
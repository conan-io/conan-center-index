from conans import ConanFile, CMake, tools
import os


class SFMLConan(ConanFile):
    name = 'sfml'
    description = 'Simple and Fast Multimedia Library'
    license = "Zlib"
    topics = ('conan', 'sfml', 'multimedia')
    homepage = 'https://github.com/SFML/SFML'
    url = 'https://github.com/conan-io/conan-center-index'
    exports_sources = ['CMakeLists.txt', 'patches/*']
    generators = 'cmake', 'cmake_find_package'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'window': [True, False],
        'graphics': [True, False],
        'network': [True, False],
        'audio': [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'window': True,
        'graphics': True,
        'network': True,
        'audio': True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        if self.options.graphics:
            self.requires('freetype/2.10.1')
            self.requires('stb/20200203')
        if self.options.audio:
            self.requires('openal/1.19.1')
            self.requires('flac/1.3.3')
            self.requires('ogg/1.3.4')
            self.requires('vorbis/1.3.6')
        if self.options.window:
            if self.settings.os in ['Linux', 'FreeBSD']:
                self.requires('xorg/system')
            self.requires('opengl/system')

    def system_requirements(self):
        if self.settings.os == 'Linux' and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                packages = []
                if self.options.window:
                    packages.extend(['libudev-dev'])
                for package in packages:
                    installer.install(package)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'SFML-' + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.rmdir(os.path.join(self._source_subfolder, "extlibs"))

    def _configure_cmake(self):
        if self._cmake:
            return self.cmake
        self.cmake = CMake(self)

        self.cmake.definitions['SFML_BUILD_WINDOW'] = self.options.window
        self.cmake.definitions['SFML_BUILD_GRAPHICS'] = self.options.graphics
        self.cmake.definitions['SFML_BUILD_NETWORK'] = self.options.network
        self.cmake.definitions['SFML_BUILD_AUDIO'] = self.options.audio

        self.cmake.definitions['SFML_INSTALL_PKGCONFIG_FILES'] = False
        self.cmake.definitions['SFML_GENERATE_PDB'] = False

        self.cmake.configure(build_folder=self._build_subfolder)
        return self.cmake

    def build(self):
        for patch in self.conan_data.get("patches",{}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        os.remove(os.path.join(self.package_folder, "license.md"))
        os.remove(os.path.join(self.package_folder, "readme.md"))

    def _get_decorated_lib(self, name):
        suffix = '-s' if not self.options.shared else ''
        suffix += '-d' if self.settings.build_type == 'Debug' else ''
        return name + suffix

    def package_info(self):

        self.cpp_info.names["cmake_find_package"] = "SFML"
        self.cpp_info.names["cmake_find_package_multi"] = "SFML"
        self.cpp_info.names["pkg_config"] = "SFML"

        self.cpp_info.components["system"].libs = [self._get_decorated_lib("sfml-system")]
        if not self.options.shared:
            self.cpp_info.components["system"].defines = ['SFML_STATIC']
        if self.settings.os == 'Windows':
            self.cpp_info.components["system"].system_libs = ['winmm']
        elif self.settings.os == 'Linux':
            self.cpp_info.components["system"].system_libs = ['rt']
        elif self.settings.os == 'Android':
            self.cpp_info.components["system"].system_libs = ['android', 'log']
        if self.settings.os != 'Windows':
            self.cpp_info.components["system"].system_libs = ['pthread']

        if self.settings.os in ['Windows', 'Android', 'iOS']:
            sfml_main_suffix = '-d' if self.settings.build_type == 'Debug' else ''
            self.cpp_info.components["main"].libs = ["sfml-main" + sfml_main_suffix]
            if not self.options.shared:
                self.cpp_info.components["main"].defines = ['SFML_STATIC']
            if self.settings.os == 'Android':
                self.cpp_info.components["main"].libs.append(self._get_decorated_lib("sfml-activity"))
                self.cpp_info.components["main"].system_libs = ['android', 'log']

        if self.options.window or self.options.graphics:
            self.cpp_info.components["window"].libs = [self._get_decorated_lib("sfml-window")]
            self.cpp_info.components["window"].requires = ["opengl::opengl", "system"]
            if self.settings.os in ['Linux', 'FreeBSD']:
                self.cpp_info.components["window"].requires.append('xorg::xorg')
            if not self.options.shared:
                self.cpp_info.components["window"].defines = ['SFML_STATIC']
            if self.settings.os == 'Windows':
                self.cpp_info.components["window"].system_libs = ['winmm', 'gdi32']
            if self.settings.os == 'Linux':
                self.cpp_info.components["window"].system_libs = ['udev']
            if self.settings.os == 'FreeBSD':
                self.cpp_info.components["window"].system_libs = ['usbhid']
            elif self.settings.os == "Macos":
                self.cpp_info.components["window"].frameworks['Foundation', 'AppKit', 'IOKit', 'Carbon']
                if not self.options.shared:
                    self.cpp_info.components["window"].exelinkflags.append("-ObjC")
                    self.cpp_info.components["window"].sharedlinkflags = self.cpp_info.components["window"].exelinkflags
            elif self.settings.os == "iOS":
                self.cpp_info.frameworks['Foundation', 'UIKit', 'CoreGraphics', 'QuartzCore', 'CoreMotion']
            elif self.settings.os == "Android":
                self.cpp_info.components["window"].system_libs = ['android']

        if self.options.graphics:
            self.cpp_info.components["graphics"].libs = [self._get_decorated_lib("sfml-graphics")]
            self.cpp_info.components["graphics"].requires = ["freetype::freetype", "stb::stb", "window"]
            if not self.options.shared:
                self.cpp_info.components["graphics"].defines = ['SFML_STATIC']
            if self.settings.os == 'Linux':
                self.cpp_info.components["graphics"].system_libs = ['udev']

        if self.options.network:
            self.cpp_info.components["network"].libs = [self._get_decorated_lib("sfml-network")]
            self.cpp_info.components["network"].requires = ["system"]
            if not self.options.shared:
                self.cpp_info.components["network"].defines = ['SFML_STATIC']
            if self.settings.os == 'Windows':
                self.cpp_info.components["network"].system_libs = ['ws2_32']

        if self.options.audio:
            self.cpp_info.components["audio"].libs = [self._get_decorated_lib("sfml-audio")]
            self.cpp_info.components["audio"].requires = ["openal::openal", "flac::flac", "ogg::ogg", "vorbis::vorbis"]
            if not self.options.shared:
                self.cpp_info.components["audio"].defines = ['SFML_STATIC']
            if self.settings.os == "Android":
                self.cpp_info.components["audio"].system_libs = ['android']

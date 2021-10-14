from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class SfmlConan(ConanFile):
    name = "sfml"
    description = "Simple and Fast Multimedia Library."
    license = "Zlib"
    topics = ("sfml", "multimedia", "games", "graphics", "audio")
    homepage = "https://www.sfml-dev.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "window": [True, False],
        "graphics": [True, False],
        "network": [True, False],
        "audio": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "window": True,
        "graphics": True,
        "network": True,
        "audio": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.window:
            if self.settings.os in ["Windows", "Linux", "FreeBSD", "Macos"]:
                self.requires("opengl/system")
            if self.settings.os == "Linux":
                self.requires("libudev/system")
                self.requires("xorg/system")
        if self.options.graphics:
            self.requires("freetype/2.11.0")
            self.requires("stb/cci.20210713")
        if self.options.audio:
            self.requires("flac/1.3.3")
            self.requires("openal/1.21.1")
            self.requires("vorbis/1.3.7")

    def validate(self):
        if self.settings.os not in ["Windows", "Linux", "FreeBSD", "Android", "Macos", "iOS"]:
            raise ConanInvalidConfiguration("SFML not supported on {}".format(self.settings.os))
        if self.options.graphics and not self.options.window:
            raise ConanInvalidConfiguration("sfml:graphics=True requires sfml:window=True")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        tools.rmdir(os.path.join(self._source_subfolder, "extlibs"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SFML_DEPENDENCIES_INSTALL_PREFIX"] = self.package_folder
        self._cmake.definitions["SFML_MISC_INSTALL_PREFIX"] = os.path.join(self.package_folder, "licenses").replace("\\", "/")
        self._cmake.definitions["SFML_BUILD_WINDOW"] = self.options.window
        self._cmake.definitions["SFML_BUILD_GRAPHICS"] = self.options.graphics
        self._cmake.definitions["SFML_BUILD_NETWORK"] = self.options.network
        self._cmake.definitions["SFML_BUILD_AUDIO"] = self.options.audio
        self._cmake.definitions["SFML_INSTALL_PKGCONFIG_FILES"] = False
        self._cmake.definitions["SFML_GENERATE_PDB"] = False
        self._cmake.definitions["SFML_USE_SYSTEM_DEPS"] = True
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["SFML_USE_STATIC_STD_LIBS"] = "MT" in self.settings.compiler.runtime
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {values["target"]: "SFML::{}".format(component) for component, values in self._sfml_components.items()}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _sfml_components(self):
        def gdi32():
            return ["gdi32"] if self.settings.os == "Windows" else []

        def winmm():
            return ["winmm"] if self.settings.os == "Windows" else []

        def ws2_32():
            return ["ws2_32"] if self.settings.os == "Windows" else []

        def libudev():
            return ["libudev::libudev"] if self.settings.os == "Linux" else []

        def xorg():
            return ["xorg::xorg"] if self.settings.os == "Linux" else []

        def pthread():
            return ["pthread"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def rt():
            return ["rt"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def usbhid():
            return ["usbhid"] if self.settings.os == "FreeBSD" else []

        def android():
            return ["android"] if self.settings.os == "Android" else []

        def log():
            return ["log"] if self.settings.os == "Android" else []

        def foundation():
            return ["Foundation"] if tools.is_apple_os(self.settings.os) else []

        def appkit():
            return ["AppKit"] if self.settings.os == "Macos" else []

        def carbon():
            return ["Carbon"] if self.settings.os == "Macos" else []

        def iokit():
            return ["IOKit"] if self.settings.os == "Macos" else []

        def coregraphics():
            return ["CoreGraphics"] if self.settings.os == "iOS" else []

        def coremotion():
            return ["CoreMotion"] if self.settings.os == "iOS" else []

        def quartzcore():
            return ["QuartzCore"] if self.settings.os == "iOS" else []

        def uikit():
            return ["UIKit"] if self.settings.os == "iOS" else []

        def opengl():
            return ["opengl::opengl"] if self.settings.os in ["Windows", "Linux", "FreeBSD", "Macos"] else []

        def opengles_android():
            return ["EGL", "GLESv1_CM"] if self.settings.os == "Android" else []

        def opengles_ios():
            return ["OpenGLES"] if self.settings.os == "iOS" else []

        suffix = "" if self.options.shared else "-s"
        suffix += "-d" if self.settings.build_type == "Debug" else ""

        sfml_components = {
            "system": {
                "target": "sfml-system",
                "libs": ["sfml-system{}".format(suffix)],
                "system_libs": winmm() + pthread() + rt() + android() + log(),
            },
        }
        if self.settings.os in ["Windows", "Android", "iOS"]:
            sfml_main_suffix = "-d" if self.settings.build_type == "Debug" else ""
            sfmlmain_libs = ["sfml-main{}".format(sfml_main_suffix)]
            if self.settings.os == "Android":
                sfmlmain_libs.append("sfml-activity{}".format(suffix))
            sfml_components.update({
                "main": {
                    "target": "sfml-main",
                    "libs": sfmlmain_libs,
                    "system_libs": android() + log(),
                },
            })
        if self.options.window:
            sfml_components.update({
                "window": {
                    "target": "sfml-window",
                    "libs": ["sfml-window{}".format(suffix)],
                    "requires": ["system"] + opengl() + xorg() + libudev(),
                    "system_libs": gdi32() + winmm() + usbhid() + android() + opengles_android(),
                    "frameworks": foundation() + appkit() + iokit() + carbon() +
                                  uikit() + coregraphics() + quartzcore() +
                                  coremotion() + opengles_ios(),
                },
            })
        if self.options.graphics:
            sfml_components.update({
                "graphics": {
                    "target": "sfml-graphics",
                    "libs": ["sfml-graphics{}".format(suffix)],
                    "requires": ["window", "freetype::freetype", "stb::stb"],
                },
            })
        if self.options.network:
            sfml_components.update({
                "network": {
                    "target": "sfml-network",
                    "libs": ["sfml-network{}".format(suffix)],
                    "requires": ["system"],
                    "system_libs": ws2_32(),
                },
            })
        if self.options.audio:
            sfml_components.update({
                "audio": {
                    "target": "sfml-audio",
                    "libs": ["sfml-audio{}".format(suffix)],
                    "requires": ["system", "flac::flac", "openal::openal", "vorbis::vorbis"],
                    "system_libs": android(),
                },
            })

        return sfml_components

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SFML"
        self.cpp_info.names["cmake_find_package_multi"] = "SFML"
        self.cpp_info.names["pkgconfig"] = "sfml-all"

        def _register_components(components):
            defines = [] if self.options.shared else ["SFML_STATIC"]
            for component, values in components.items():
                target = values.get("target", [])
                libs = values.get("libs", [])
                requires = values.get("requires", [])
                system_libs = values.get("system_libs", [])
                frameworks = values.get("frameworks", [])
                self.cpp_info.components[component].names["cmake_find_package"] = component
                self.cpp_info.components[component].names["cmake_find_package_multi"] = component
                self.cpp_info.components[component].names["pkg_config"] = target
                self.cpp_info.components[component].builddirs.append(self._module_subfolder)
                self.cpp_info.components[component].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[component].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                self.cpp_info.components[component].libs = libs
                self.cpp_info.components[component].defines = defines
                self.cpp_info.components[component].requires = requires
                self.cpp_info.components[component].system_libs = system_libs
                self.cpp_info.components[component].frameworks = frameworks

        _register_components(self._sfml_components)

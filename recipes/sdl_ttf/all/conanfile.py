from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SdlttfConan(ConanFile):
    name = "sdl_ttf"
    description = "A TrueType font library for SDL"
    license = "Zlib"
    topics = ("sdl2", "sdl2_ttf", "sdl", "sdl_ttf", "ttf", "font")
    homepage = "https://www.libsdl.org/projects/SDL_ttf"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("freetype/2.10.4")
        self.requires("sdl/2.0.16")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("sdl_ttf shared is not supported with Visual Studio")
        # TODO: check that major version of sdl_tff is the same than sdl (not possible yet in validate())

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # Handle sdl2 static target
        if not self.options["sdl"].shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "SDL2::SDL2", "SDL2::SDL2-static")
        # missing from distribution (only in 2.0.15?)
        tools.save(os.path.join(self._source_subfolder, "SDL2_ttfConfig.cmake"), "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "SDL2_ttf.framework"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SDL2_ttf"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_ttf"
        self.cpp_info.names["pkg_config"] = "SDL2_ttf"
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.libs = ["SDL2_ttf"]
        self.cpp_info.requires = ["freetype::freetype", "sdl::libsdl2"]

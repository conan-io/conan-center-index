from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


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

    generators = "cmake", "cmake_find_package"
    _cmake = None

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("freetype/2.11.1")
        self.requires("sdl/2.0.18")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("sdl_ttf shared is not supported with Visual Studio")
        # TODO: check that major version of sdl_tff is the same than sdl (not possible yet in validate())

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        # missing from distribution (only in 2.0.15?)
        tools.files.save(self, os.path.join(self._source_subfolder, "SDL2_ttfConfig.cmake"), "")

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
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "SDL2_ttf.framework"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL2_ttf")
        self.cpp_info.set_property("cmake_target_name", "SDL2_ttf::SDL2_ttf")
        self.cpp_info.set_property("pkg_config_name", "SDL2_ttf")

        self.cpp_info.names["cmake_find_package"] = "SDL2_ttf"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_ttf"
        self.cpp_info.names["pkg_config"] = "SDL2_ttf"

        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.libs = ["SDL2_ttf"]
        self.cpp_info.requires = ["freetype::freetype", "sdl::libsdl2"]

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SdlnetConan(ConanFile):
    name = "sdl_net"
    description = "A networking library for SDL"
    license = "Zlib"
    topics = ("sdl2", "sdl2_net", "sdl", "sdl_net", "net", "networking")
    homepage = "https://www.libsdl.org/projects/SDL_net"
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
        self.requires("sdl/2.0.16")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("sdl_net is not supported with Visual Studio")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        
        return self._cmake

    def build(self):
        # FIXME: check that major version of sdl_net is the same than sdl (not possible yet in validate())
        if tools.scm.Version(self.deps_cpp_info["sdl"].version).major != tools.scm.Version(self.version).major:
            raise ConanInvalidConfiguration(f"The major versions of {self.name} and sdl must be the same")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["SDL2_net"]
        self.cpp_info.names["cmake_find_package"] = "SDL2_net"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_net"
        self.cpp_info.names["pkg_config"] = "SDL2_net"
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])

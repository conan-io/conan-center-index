from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class LibnoiseConan(ConanFile):
    name = "libnoise"
    description = (
        "A general-purpose library that generates three-dimensional coherent "
        "noise. Useful for terrain generation and procedural texture "
        "generation. Uses a broad number of techniques (Perlin noise, ridged "
        "multifractal, etc.) and combinations of those techniques."
    )
    license = "LGPL-2.1-or-later"
    topics = ("libnoise", "graphics", "noise-generator")
    homepage = "http://libnoise.sourceforge.net"
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
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["noise"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

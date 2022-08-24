from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class LodepngConan(ConanFile):
    name = "lodepng"
    description = "PNG encoder and decoder in C and C++, without dependencies."
    license = "Zlib"
    topics = ("png", "encoder", "decoder")
    homepage = "https://github.com/lvandeve/lodepng"
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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_vc_static_runtime(self):
        return (self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime) or \
               (str(self.settings.compiler) == "msvc" and self.settings.compiler.runtime == "static")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.options.shared and self._is_vc_static_runtime:
            raise ConanInvalidConfiguration("lodepng shared doesn't support Visual Studio with static runtime")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["lodepng"]

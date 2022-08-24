from from conan import ConanFile
from conan import ConanFile
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class RectangleBinPackConan(ConanFile):
    name = "rectanglebinpack"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/juj/RectangleBinPack"
    description = "The code can be used to solve the problem of packing a set of 2D rectangles into a larger bin."
    topics = ("rectangle", "packing", "bin")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][0],
                  strip_root=True, destination=self._source_subfolder)
        tools.files.download(self, filename="LICENSE", **self.conan_data["sources"][self.version][1])

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy("*.h", dst=os.path.join("include", self.name), src=self._source_subfolder, excludes="old/**")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["RectangleBinPack"]
        self.cpp_info.names["cmake_find_package"] = "RectangleBinPack"
        self.cpp_info.names["cmake_find_package_multi"] = "RectangleBinPack"

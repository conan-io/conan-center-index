from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from glob import glob
import os



class SshtConan(ConanFile):
    name = "ssht"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astro-informatics/ssht"
    description = "Fast spin spherical harmonic transforms"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("physics", "astrophysics", "radio interferometry")
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    requires = "fftw/3.3.9"
    generators = "cmake", "cmake_find_package", "cmake_paths"
    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("SSHT requires C99 support for complex numbers.")
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob('ssht-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def cmake(self):
        if not hasattr(self, "_cmake"):
            self._cmake = CMake(self)
            self._cmake.definitions["tests"] = False
            self._cmake.definitions["python"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self.cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ssht"]

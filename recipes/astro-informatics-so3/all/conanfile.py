from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from glob import glob
import os


class AstroInformaticsSO3(ConanFile):
    name = "astro-informatics-so3"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astro-informatics/so3"
    description = "Fast and accurate Wigner transforms"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("physics", "astrophysics", "radio interferometry")
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    requires = "fftw/3.3.9", "ssht/1.3.7"
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration(
                "SO3 requires C99 support for complex numbers."
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob("so3-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def cmake(self):
        if not hasattr(self, "_cmake"):
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_TESTING"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self.cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["astro-informatics-so3"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException


class ConanRecipe(ConanFile):
    name = "roaring"

    description = "Portable Roaring bitmaps in C and C++"
    topics = ("conan", "bitset", "compression", "index", "format")

    homepage = "https://github.com/RoaringBitmap/CRoaring"
    url = "https://github.com/conan-io/conan-center-index"

    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True}
    _cmake = None

    @property
    def _source_subfolder(self):
          return "source_subfolder"

    @property
    def _build_subfolder(self):
          return "build_subfolder"

    @property
    def _supported_cppstd(self):
        return ["11", "gnu11", "14", "gnu14", "17", "gnu17", "20", "gnu20"]


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd and \
           not self.settings.compiler.cppstd in self._supported_cppstd:
          raise ConanInvalidConfiguration("This library requires c++11 standard or higher."
                                          " {} required."
                                          .format(self.settings.compiler.cppstd))


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "CRoaring-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions['ENABLE_ROARING_TESTS'] = False
        self._cmake.definitions['ROARING_BUILD_STATIC'] = not self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ['roaring']

import os
import glob
from conans import ConanFile, CMake, tools


class ConanJBig(ConanFile):
    name = "jbig"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ImageMagick/jbig"
    description = "jbig for the Windows build of ImageMagick"
    topics = ("conan", "jbig", "imagemagick", "window", "graphic")
    license = "GPL-2.0"
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        for extracted_dir in glob.glob("jbig-*"):
            os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        self.cpp_info.libs = [self.name]

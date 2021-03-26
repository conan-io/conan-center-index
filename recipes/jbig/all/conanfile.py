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
    exports_sources = ['CMakeLists.txt', "*.patch"]
    generators = 'cmake'
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executables": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executables": True
    }

    _cmake = None

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
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXECUTABLES"] = self.options.build_executables
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = [self.name]
        if self.options.shared and self.settings.compiler == "Visual Studio":
            self.cpp_info.defines = ["_JBIGDLL_"]

        if self.options.build_executables:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

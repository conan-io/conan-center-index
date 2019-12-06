import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanException


class MinizipConan(ConanFile):
    name = "minizip"
    version = "1.2.11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = "An experimental package to read and write files in .zip format, written on top of zlib"
    topics = ("zip", "compression", "inflate")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt", "CMakeLists_minizip.txt", "minizip.patch"]
    requires = ("zlib/1.2.11")
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minizip_folder(self):
        return os.path.join(self._source_subfolder, 'contrib', 'minizip')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zlib-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._minizip_folder)
        return cmake

    def build(self):
        tools.patch(patch_file="minizip.patch", base_path=self._source_subfolder)
        os.rename("CMakeLists_minizip.txt", os.path.join(self._minizip_folder, 'CMakeLists.txt'))
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            tmp = tools.load("zlib.h")
            license_contents = tmp[2:tmp.find("*/", 1)]
            tools.save("LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["minizip"]
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append('MINIZIP_DLL')


import os
import shutil
from conans import ConanFile, tools, CMake


class MinizipConan(ConanFile):
    name = "minizip"
    version = "1.2.11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = "An experimental package to read and write files in .zip format, written on top of zlib"
    topics = ("zip", "compression", "inflate")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "bzip2": [True, False], "tools": [True, False]}
    default_options = {"shared": False, "fPIC": True, "bzip2": True, "tools": False}
    exports_sources = ["CMakeLists.txt", "*.patch"]
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.bzip2:
            self.requires("bzip2/1.0.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zlib-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_BZIP2"] = self.options.bzip2
        cmake.definitions["BUILD_TOOLS"] = self.options.tools
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        tools.patch(patch_file="minizip.patch", base_path=self._source_subfolder)
        shutil.move("CMakeLists.txt", os.path.join(self._source_subfolder, 'CMakeLists.txt'))
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
        self.cpp_info.includedirs = ["include", os.path.join("include", "minizip")]
        if self.options.bzip2:
            self.cpp_info.defines.append('HAVE_BZIP2')

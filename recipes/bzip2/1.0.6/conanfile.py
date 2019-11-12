import os
from conans import ConanFile, CMake, tools


class Bzip2Conan(ConanFile):
    name = "bzip2"
    version = "1.0.6"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bzip.org"    
    license = "bzip2-1.0.6"
    description = "bzip2 is a free and open-source file compression program that uses the Burrows Wheeler algorithm."
    topics = ("conan", "bzip2", "data-compressor", "file-compression")
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "build_executable": [True, False]}
    default_options = {"shared": False, "fPIC": True, "build_executable": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        folder_name = "%s-%s" % (self.name, self.version)
        os.rename(folder_name, self._source_subfolder)

    def _configure_cmake(self):
        major = self.version.split(".")[0]
        cmake = CMake(self)
        cmake.definitions["BZ2_VERSION_STRING"] = self.version
        cmake.definitions["BZ2_VERSION_MAJOR"] = major
        cmake.definitions["BZ2_BUILD_EXE"] = "ON" if self.options.build_executable else "OFF"
        cmake.configure()
        return cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "bzip2.c"), r"<sys\stat.h>", "<sys/stat.h>")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.name = "BZip2"
        self.cpp_info.libs = ['bz2']

import os

from conans import ConanFile, CMake, tools


class KaitaiStructCppStlRuntimeConan(ConanFile):
    name = "kaitai_struct_cpp_stl_runtime"
    version = "0.9"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://kaitai.io/"
    description = "kaitai struct c++ runtime library"
    topics = ("parsers", "streams", "dsl")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)
       

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()


    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._cmake


    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)



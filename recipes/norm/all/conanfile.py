from conans import ConanFile, CMake, tools
import os
import glob


class NormConan(ConanFile):
    name = "norm"
    description = "A reliable multicast transport protocol"
    topics = ("conan", "norm", "multicast", "transport protocol")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nrl.navy.mil/itd/ncs/products/norm"
    exports_sources = ["LICENSE"]
    generators = "cmake", "cmake_find_package"
    _cmake = None
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = self.name + "-" + os.path.splitext(os.path.basename(url))[0]
        os.rename(extracted_dir, self._source_subfolder)
        
    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._cmake
 
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        
    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "RapidJSON"
        self.cpp_info.names["cmake_find_package_multi"] = "RapidJSON"

from conans import ConanFile, CMake, tools
import os
import glob


class NormConan(ConanFile):
    name = "norm"
    description = "A reliable multicast transport protocol"
    topics = ("conan", "norm", "multicast", "transport protocol")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nrl.navy.mil/itd/ncs/products/norm"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None
    license = "NRL"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = self.name + "-" + \
            os.path.splitext(os.path.basename(url))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NORM_CUSTOM_PROTOLIB_VERSION"] = self.conan_data["protolib"][self.version]["githash"]
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "norm"
        self.cpp_info.names["cmake_find_package_multi"] = "norm"
        self.cpp_info.libs = tools.collect_libs(self)
        if(self.settings.os == "Windows"):
            self.cpp_info.system_libs = [
                "ws2_32", "iphlpapi", "user32", "gdi32", "Advapi32", "ntdll"]
        else:
            self.cpp_info.system_libs = ["pthread"]
        if(self.settings.os == "Linux"):
            self.cpp_info.system_libs.append(["dl rt"])

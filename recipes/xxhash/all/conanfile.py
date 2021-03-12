import os
from conans import ConanFile, CMake, tools


class XxHash(ConanFile):
    name = "xxhash"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Cyan4973/xxHash"
    description = "Extremely fast non-cryptographic hash algorithm"
    topics = ("conan", "hash", "algorithm", "fast", "checksum", "hash-functions")
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "xxHash-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=os.path.join(self._source_subfolder, "cmake_unofficial"))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["main"].names["cmake_find_package"] = "xxhash"
        self.cpp_info.components["main"].names["cmake_find_package_multi"] = "sxxhash"
        self.cpp_info.components["main"].libs = ["xxhash"]

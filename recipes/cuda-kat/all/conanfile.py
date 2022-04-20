from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class CudaKatConan(ConanFile):
    name = "cuda-kat"
    homepage = "https://github.com/eyalroz/cuda-kat"
    description = "CUDA kernel author's tools"
    topics = ("gpgpu", "cuda", "cuda-kat", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("CUDA-kat library are not compatible on Windows")
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)


    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=os.path.join(self._source_subfolder, "src"), dst="include")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cuda-kat"
        self.cpp_info.names["cmake_find_package_multi"] = "cuda-kat"

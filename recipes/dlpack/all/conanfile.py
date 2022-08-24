import os
from conans import ConanFile, tools

required_conan_version = ">=1.33.0"


class DlpackConan(ConanFile):
    name = "dlpack"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dmlc/dlpack"
    description = "RFC for common in-memory tensor structure and operator interface for deep learning system"
    topics = ("conan", "dlpack", "tensor", "operator")
    no_copy_source = True

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy("*dlpack.h", keep_path=True)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.libdirs = []

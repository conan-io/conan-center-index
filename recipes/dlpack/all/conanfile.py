import os
from conan import ConanFile
from conan.tools.files import copy, get

required_conan_version = ">=1.33.0"


class DlpackConan(ConanFile):
    name = "dlpack"
    package_type = "header-library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dmlc/dlpack"
    description = "RFC for common in-memory tensor structure and operator interface for deep learning system"
    topics = ("dlpack", "tensor", "operator")
    no_copy_source = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst="licenses")
        copy(
            self,
            pattern="*.h",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

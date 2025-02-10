import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, replace_in_file
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


class GpuCppConan(ConanFile):
    name = "gpu.cpp"
    description = "A lightweight library for portable low-level GPU computation using WebGPU."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gpucpp.answer.ai/"
    topics = ("gpgpu", "webgpu")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("dawn/cci.20240726")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        pkg_includes = os.path.join(self.package_folder, "include", "gpu.cpp")
        copy(self, "gpu.h", self.source_folder, pkg_includes)
        copy(self, "*.h", os.path.join(self.source_folder, "numeric_types"), os.path.join(pkg_includes, "numeric_types"))
        copy(self, "*.h", os.path.join(self.source_folder, "utils"), os.path.join(pkg_includes, "utils"))

        # Fix incompatibility with newer Dawn
        replace_in_file(self, os.path.join(pkg_includes, "gpu.h"),
                        "WGPUBufferUsageFlags",
                        "WGPUBufferUsage")

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

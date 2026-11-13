from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=2.0"

class QuillConan(ConanFile):
    name = "quill"
    description = "Asynchronous Low Latency C++ Logging Library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/odygrd/quill/"
    topics = ("logging", "log", "async", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        supported_archs = ["x86", "x86_64", "armv6", "armv7", "armv7hf", "armv8"]

        if not any(arch in str(self.settings.arch) for arch in supported_archs):
            raise ConanInvalidConfiguration(f"{self.settings.arch} is not supported by {self.ref}")

        check_min_cppstd(self, 17)

        if self.settings.compiler== "clang" and Version(self.settings.compiler.version).major == "11" and \
            self.settings.compiler.libcxx == "libstdc++":
            raise ConanInvalidConfiguration(f"{self.ref} requires C++ filesystem library, which your compiler doesn't support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("rt")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")

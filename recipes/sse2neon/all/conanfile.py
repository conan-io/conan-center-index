from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "sse2neon"
    description = "A translator from Intel SSE intrinsics to Arm/Aarch64 NEON implementation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DLTcollab/sse2neon"
    topics = ("sse2", "neon", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        arch = str(self.settings.arch)
        if not arch.startswith("armv7") and not arch.startswith("armv8") and not arch.startswith("arm64"):
            raise ConanInvalidConfiguration(f"{self.ref} can only be used for ARM NEON architectures.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "sse2neon.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.52.0"


class SIMEeConan(ConanFile):
    name = "simde"
    description = "Implementations of SIMD instruction sets for systems which don't natively support them."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/simd-everywhere/simde"
    topics = ("neon", "avx", "sse", "simd", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.arch not in ["x86", "x86_64", "armv8"] or self.settings.os == "Emscripten":
            raise ConanInvalidConfiguration(f"{self.ref} supports x86, x86_64, armv8 only or emscriptien.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include", "simde"),
            src=os.path.join(self.source_folder, "simde"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("pkg_config_name", "SIMDe")

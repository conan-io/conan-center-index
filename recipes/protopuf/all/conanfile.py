from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import os


required_conan_version = ">=2.1"


class ProtopufConan(ConanFile):
    name = "protopuf"
    description = "Protocol Puffers: A little, highly templated, and protobuf-compatible serialization/deserialization header-only library written in C++20"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/PragmaTwice/protopuf"
    topics = ("serialization", "protobuf", "metaprogramming", "header-only")
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "17":
            # there are specific C++20 features used in this library that require apple-clang 17 or higher
            raise ConanInvalidConfiguration(
                f"apple-clang 17 or higher is required"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

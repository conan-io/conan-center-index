from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, download
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class CistaConan(ConanFile):
    name = "cista"
    description = (
        "Cista++ is a simple, open source (MIT license) C++17 "
        "compatible way of (de-)serializing C++ data structures."
    )
    license = "MIT"
    topics = ("cista", "serialization", "deserialization", "reflection")
    homepage = "https://github.com/felixguendling/cista"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "8",
            "clang": "6",
            "apple-clang": "9.1"
        }

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), None)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++17, which your compiler does not support.",
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        for file in self.conan_data["sources"][self.version]:
            filename = os.path.basename(file["url"])
            download(self, filename=filename, **file)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "cista.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cista")
        self.cpp_info.set_property("cmake_target_name", "cista::cista")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

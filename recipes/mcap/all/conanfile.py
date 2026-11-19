from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.4"

class McapConan(ConanFile):
    name = "mcap"
    description = (
        "MCAP is a modular, performant, and serialization-agnostic container file format for pub/sub messages, "
        "primarily intended for use in robotics applications."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/mcap"
    topics = ("serialization", "deserialization", "recording", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_package_path(self):
        return os.path.join(self.source_folder, "cpp", "mcap")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("lz4/[>=1.9.4 <2]")
        self.requires("zstd/[>=1.5 <1.6]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._source_package_path)
        copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self._source_package_path, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

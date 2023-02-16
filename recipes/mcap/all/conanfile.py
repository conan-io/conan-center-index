from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

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
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "191",
            "gcc": "9",
            "clang": "9",
            "apple-clang": "12",
        }

    @property
    def _source_package_path(self):
        return os.path.join(self.source_folder, "cpp", "mcap")

    def configure(self):
        if Version(self.version) < "0.3.0":
            self.license = "Apache-2.0"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("lz4/1.9.4")
        self.requires("zstd/1.5.2")
        if Version(self.version) < "0.1.1":
            self.requires("fmt/9.1.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if Version(self.version) < "0.1.1" and is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio compiler has been supported since 0.1.1")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._source_package_path)
        copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self._source_package_path, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

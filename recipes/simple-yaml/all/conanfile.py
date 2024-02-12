import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class SimpleYamlConan(ConanFile):
    name = "simple-yaml"
    description = "Read configuration files in YAML format by code structure"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Rechip/simple-yaml"
    topics = ("cpp", "yaml", "configuration", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_enum": [True, False],
    }
    default_options = {
        "enable_enum": True,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "10",
            "clang": "11",
            "apple-clang": "13.3",
            "msvc": "193",
            "Visual Studio": "16.3",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("pretty-name/1.0.0")
        self.requires("yaml-cpp/0.8.0")
        self.requires("source_location/0.2.1")
        if self.options.enable_enum:
            self.requires("magic_enum/0.9.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if (
            self.settings.compiler == "clang"
            and self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"]
            and self.settings.compiler.version == "11"
        ):
            raise ConanInvalidConfiguration(
                "clang 11 with libstdc++ is not supported due to old libstdc++ missing C++17 support"
            )
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning("simple-yaml requires C++20. Your compiler is unknown. Assuming it fully supports C++20.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("simple-yaml requires C++20, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class SerdeppConan(ConanFile):
    name = "serdepp"
    description = "c++ serialize and deserialize adaptor library like rust serde.rs"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/injae/serdepp"
    topics = ("yaml", "toml", "serialization", "json", "reflection", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_nlohmann_json": [True, False],
        "with_rapidjson": [True, False],
        "with_fmt": [True, False],
        "with_toml11": [True, False],
        "with_yamlcpp": [True, False],
    }
    default_options = {
        "with_nlohmann_json": True,
        "with_rapidjson": True,
        "with_fmt": True,
        "with_toml11": True,
        "with_yamlcpp": True,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "17",
            "clang": "5",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nameof/0.10.3")
        self.requires("magic_enum/0.9.5")
        if self.options.with_toml11:
            self.requires("toml11/3.8.1")
        if self.options.with_yamlcpp:
            self.requires("yaml-cpp/0.8.0")
        if self.options.with_rapidjson:
            self.requires("rapidjson/1.1.0")
        if self.options.with_fmt:
            self.requires("fmt/10.2.1")
        if self.options.with_nlohmann_json:
            self.requires("nlohmann_json/3.11.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)

        if not minimum_version:
            self.output.warning(f"{self.name} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires a compiler that supports at least C++{self._min_cppstd}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        s = lambda x: os.path.join(self.source_folder, x)
        p = lambda x: os.path.join(self.package_folder, x)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        include = os.path.join("include", "serdepp")
        copy(self, "*.hpp", dst=p(include), src=s(include))
        attribute = os.path.join(include, "attribute")
        copy(self, "*.hpp", dst=p(attribute), src=s(attribute))
        adaptor = os.path.join(include, "adaptor")
        copy(self, "reflection.hpp", dst=p(adaptor), src=s(adaptor))
        copy(self, "sstream.hpp", dst=p(adaptor), src=s(adaptor))
        if self.options.with_toml11:
            copy(self, "toml11.hpp", dst=p(adaptor), src=s(adaptor))
        if self.options.with_yamlcpp:
            copy(self, "yaml-cpp.hpp", dst=p(adaptor), src=s(adaptor))
        if self.options.with_rapidjson:
            copy(self, "rapidjson.hpp", dst=p(adaptor), src=s(adaptor))
        if self.options.with_fmt:
            copy(self, "fmt.hpp", dst=p(adaptor), src=s(adaptor))
        if self.options.with_nlohmann_json:
            copy(self, "nlohmann_json.hpp", dst=p(adaptor), src=s(adaptor))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

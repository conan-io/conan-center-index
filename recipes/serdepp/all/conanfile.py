import os

from conan.errors import ConanInvalidConfiguration
from conans import ConanFile, tools

required_conan_version = ">=1.43.0"


class SerdeppConan(ConanFile):
    name = "serdepp"
    description = "c++ serialize and deserialize adaptor library like rust serde.rs"
    license = "MIT"
    topics = ("yaml", "toml", "serialization", "json", "reflection")
    homepage = "https://github.com/injae/serdepp"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "arch", "build_type", "compiler", "os"
    options = {
        # keeping the option in case upstream support dynamic linking
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
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder,
                  strip_root=True)

    def package_id(self):
        self.info.header_only()

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "17",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)

        if not minimum_version:
            self.output.warn(f"{self.name} requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires a compiler that supports at least C++17")

    def package(self):
        s = lambda x: os.path.join(self._source_subfolder, x)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        include = os.path.join('include', 'serdepp')
        self.copy('*.hpp', dst=include, src=s(include))
        attribute = os.path.join(include, 'attribute')
        self.copy('*.hpp', dst=attribute, src=s(attribute))
        adaptor = os.path.join(include, 'adaptor')
        self.copy('reflection.hpp', dst=adaptor, src=s(adaptor))
        self.copy('sstream.hpp', dst=adaptor, src=s(adaptor))
        if self.options.with_toml11:
            self.copy('toml11.hpp', dst=adaptor, src=s(adaptor))
        if self.options.with_yamlcpp:
            self.copy('yaml-cpp.hpp', dst=adaptor, src=s(adaptor))
        if self.options.with_rapidjson:
            self.copy('rapidjson.hpp', dst=adaptor, src=s(adaptor))
        if self.options.with_fmt:
            self.copy('fmt.hpp', dst=adaptor, src=s(adaptor))
        if self.options.with_nlohmann_json:
            self.copy('nlohmann_json.hpp', dst=adaptor, src=s(adaptor))

    def requirements(self):
        self.requires("nameof/0.10.1")
        self.requires("magic_enum/0.7.3")
        if self.options.with_toml11:
            self.requires("toml11/3.7.0")
        if self.options.with_yamlcpp:
            self.requires("yaml-cpp/0.7.0")
        if self.options.with_rapidjson:
            self.requires("rapidjson/1.1.0")
        if self.options.with_fmt:
            self.requires("fmt/8.1.1")
        if self.options.with_nlohmann_json:
            self.requires("nlohmann_json/3.10.5")

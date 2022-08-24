import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class SimpleYamlConan(ConanFile):
    name = "simple-yaml"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Rechip/simple-yaml"
    description = "Read configuration files in YAML format by code structure"
    topics = ("cpp", "yaml", "configuration")
    settings = ["compiler"]
    no_copy_source = True

    options = {
        "enable_enum": [True, False],
    }
    default_options = {
        "enable_enum": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("pretty-name/1.0.0")
        self.requires("yaml-cpp/0.7.0")
        self.requires("source_location/0.2.0")
        if self.options.enable_enum:
            self.requires("magic_enum/0.7.3")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16.3",
            "gcc": "10",
            "clang": "11",
            "apple-clang": "13.3",
        }

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "20")
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] and self.settings.compiler.version == "11":
            raise ConanInvalidConfiguration("clang 11 with libstdc++ is not supported due to old libstdc++ missing C++17 support")
        minimum_version = self._minimum_compilers_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "simple-yaml requires C++20. Your compiler is unknown. Assuming it fully supports C++20.")
        elif tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "simple-yaml requires C++20, which your compiler does not support.")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "simple-yaml"
        self.cpp_info.names["cmake_find_package_multi"] = "simple-yaml"

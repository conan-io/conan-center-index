from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.43.0"

class RapidYAMLConan(ConanFile):
    name = "rapidyaml"
    description = "a library to parse and emit YAML, and do it fast."
    topics = ("yaml", "parser", "emitter")
    license = "MIT",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/biojppm/rapidyaml"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_default_callbacks": [True, False],
        "with_tab_tokens": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_default_callbacks": True,
        "with_tab_tokens": False,
    }
    generators = "cmake", "cmake_find_package_multi"

    _compiler_required_cpp11 = {
        "Visual Studio": "13",
        "gcc": "6",
        "clang": "4",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "0.4.0":
            del self.options.with_tab_tokens

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("c4core/0.1.9")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

        minimum_version = self._compiler_required_cpp11.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++11, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++11. Your compiler is unknown. Assuming it supports C++11.".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["RYML_DEFAULT_CALLBACKS"] = self.options.with_default_callbacks
        if tools.Version(self.version) >= "0.4.0":
            cmake.definitions["RYML_WITH_TAB_TOKENS"] = self.options.with_tab_tokens
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "include"), "*.natvis")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ryml")
        self.cpp_info.set_property("cmake_target_name", "ryml::ryml")
        self.cpp_info.libs = ["ryml"]

        self.cpp_info.names["cmake_find_package"] = "ryml"
        self.cpp_info.names["cmake_find_package_multi"] = "ryml"

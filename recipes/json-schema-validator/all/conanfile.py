from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class JsonSchemaValidatorConan(ConanFile):
    name = "json-schema-validator"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pboettch/json-schema-validator"
    description = "JSON schema validator for JSON for Modern C++ "
    topics = ("json-schema-validator", "modern-json",
              "schema-validation", "json")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("nlohmann_json/3.10.5")

    def validate(self):
        version = tools.Version(self.version)
        min_vs_version = "16" if version < "2.1.0" else "14"
        min_cppstd = "17" if self.settings.compiler == "Visual Studio" and version < "2.1.0" else "11"
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, min_cppstd)
            min_vs_version = "15" if version < "2.1.0" else "14"

        compilers = {
            "Visual Studio": min_vs_version,
            "gcc": "5" if version < "2.1.0" else "4.9",
            "clang": "4",
            "apple-clang": "9"}
        min_version = compilers.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires c++{} support. The current compiler {} {} does not support it.".format(
                    self.name, min_cppstd, self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        if tools.Version(self.version) < "2.1.0":
            self._cmake.definitions["NLOHMANN_JSON_DIR"] = ";".join(self.deps_cpp_info["nlohmann_json"].include_paths)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if tools.Version(self.version) < "2.1.0":
            self.copy("json-schema.hpp",
                      dst=os.path.join("include", "nlohmann"),
                      src=os.path.join(self._source_subfolder, "src"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"nlohmann_json_schema_validator": "nlohmann_json_schema_validator::nlohmann_json_schema_validator"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nlohmann_json_schema_validator")
        self.cpp_info.set_property("cmake_target_name", "nlohmann_json_schema_validator")
        self.cpp_info.libs = ["json-schema-validator" if tools.Version(self.version) < "2.1.0" else "nlohmann_json_schema_validator"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "nlohmann_json_schema_validator"
        self.cpp_info.names["cmake_find_package_multi"] = "nlohmann_json_schema_validator"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

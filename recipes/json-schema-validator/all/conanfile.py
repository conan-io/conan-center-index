from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import build, files, scm
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.50.0"


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
        self.requires("nlohmann_json/3.11.2")

    def validate(self):
        version = scm.Version(self.version)
        min_vs_version = "16" if version < "2.1.0" else "14"
        min_cppstd = "17" if self.settings.compiler == "Visual Studio" and version < "2.1.0" else "11"
        if self.settings.get_safe("compiler.cppstd"):
            build.check_min_cppstd(self, min_cppstd)
            min_vs_version = "15" if version < "2.1.0" else "14"

        compilers = {
            "Visual Studio": min_vs_version,
            "gcc": "5" if version < "2.1.0" else "4.9",
            "clang": "4",
            "apple-clang": "9"}
        min_version = compilers.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if scm.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires c++{min_cppstd} support. The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        if scm.Version(self.version) < "2.1.0":
            self._cmake.definitions["NLOHMANN_JSON_DIR"] = ";".join(self.deps_cpp_info["nlohmann_json"].include_paths)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        files.copy(self, "LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if scm.Version(self.version) < "2.1.0":
            files.copy(self, "json-schema.hpp",
                       dst=os.path.join("include", "nlohmann"),
                       src=os.path.join(self._source_subfolder, "src"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"nlohmann_json_schema_validator": "nlohmann_json_schema_validator::nlohmann_json_schema_validator"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nlohmann_json_schema_validator")
        self.cpp_info.set_property("cmake_target_name", "nlohmann_json_schema_validator")
        self.cpp_info.libs = ["json-schema-validator" if scm.Version(self.version) < "2.1.0" else "nlohmann_json_schema_validator"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "nlohmann_json_schema_validator"
        self.cpp_info.names["cmake_find_package_multi"] = "nlohmann_json_schema_validator"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

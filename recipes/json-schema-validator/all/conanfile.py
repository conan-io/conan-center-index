from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import build, files, microsoft, scm
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os
import textwrap

required_conan_version = ">=1.53.0"


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

    def export_sources(self):
        files.export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("nlohmann_json/3.11.2", transitive_headers=True)

    def validate(self):
        version = scm.Version(self.version)
        min_vs_version = "16" if version < "2.1.0" else "14"
        min_cppstd = "17" if microsoft.is_msvc(self) and version < "2.1.0" else "11"
        if self.info.settings.get_safe("compiler.cppstd"):
            build.check_min_cppstd(self, min_cppstd)
            min_vs_version = "15" if version < "2.1.0" else "14"

        compilers = {
            "Visual Studio": min_vs_version,
            "gcc": "5" if version < "2.1.0" else "4.9",
            "clang": "4",
            "apple-clang": "9"}
        min_version = compilers.get(str(self.info.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the {self.info.settings.compiler} compiler support.")
        else:
            if scm.Version(self.info.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires c++{min_cppstd} support. The current compiler {self.info.settings.compiler} {self.info.settings.compiler.version} does not support it.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if scm.Version(self.version) < "2.2.0":
            tc.variables["BUILD_TESTS"] = False
            tc.variables["BUILD_EXAMPLES"] = False
        else:
            tc.variables["JSON_VALIDATOR_BUILD_TESTS"] = False
            tc.variables["JSON_VALIDATOR_BUILD_EXAMPLES"] = False
        if scm.Version(self.version) < "2.1.0":
            tc.variables["NLOHMANN_JSON_DIR"] = ";".join(self.deps_cpp_info["nlohmann_json"].include_paths).replace("\\", "/")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        files.copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        if scm.Version(self.version) < "2.1.0":
            files.copy(self, "json-schema.hpp",
                       dst=os.path.join(self.package_folder, "include", "nlohmann"),
                       src=os.path.join(self.source_folder, "src"))
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

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "nlohmann_json_schema_validator"
        self.cpp_info.names["cmake_find_package_multi"] = "nlohmann_json_schema_validator"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

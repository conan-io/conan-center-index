from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class JsonSchemaValidatorConan(ConanFile):
    name = "json-schema-validator"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pboettch/json-schema-validator"
    description = "JSON schema validator for JSON for Modern C++ "
    topics = ("modern-json", "schema-validation", "json")
    package_type = "library"
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

    @property
    def _min_cppstd(self):
        return "17" if is_msvc(self) and Version(self.version) < "2.1.0" else "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15" if Version(self.version) < "2.1.0" else "14",
            "msvc": "191" if Version(self.version) < "2.1.0" else "190",
            "gcc": "5" if Version(self.version) < "2.1.0" else "4.9",
            "clang": "4",
            "apple-clang": "9"
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/3.11.2", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "2.2.0":
            tc.variables["BUILD_TESTS"] = False
            tc.variables["BUILD_EXAMPLES"] = False
        else:
            tc.variables["JSON_VALIDATOR_BUILD_TESTS"] = False
            tc.variables["JSON_VALIDATOR_BUILD_EXAMPLES"] = False
        if Version(self.version) < "2.1.0":
            nlohmann_json_includedirs = self.dependencies["nlohmann_json"].cpp_info.aggregated_components().includedirs
            tc.variables["NLOHMANN_JSON_DIR"] = ";".join([p.replace("\\", "/") for p in nlohmann_json_includedirs])
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if Version(self.version) < "2.1.0":
            copy(self, "json-schema.hpp",
                       dst=os.path.join(self.package_folder, "include", "nlohmann"),
                       src=os.path.join(self.source_folder, "src"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"nlohmann_json_schema_validator": "nlohmann_json_schema_validator::nlohmann_json_schema_validator"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nlohmann_json_schema_validator")
        self.cpp_info.set_property("cmake_target_name", "nlohmann_json_schema_validator")
        self.cpp_info.libs = ["json-schema-validator" if Version(self.version) < "2.1.0" else "nlohmann_json_schema_validator"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "nlohmann_json_schema_validator"
        self.cpp_info.names["cmake_find_package_multi"] = "nlohmann_json_schema_validator"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class JsonSchemaValidatorConan(ConanFile):
    name = "json-schema-validator"
    description = "JSON schema validator for JSON for Modern C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pboettch/json-schema-validator"
    topics = ("modern-json", "schema-validation", "json")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "json_diagnostics": [True, False],
    }
    options_description = {
        "json_diagnostics": (
            "Defines JSON_DIAGNOSTICS=1 for the nlohmann_json library. "
            "Refer https://json.nlohmann.me/api/macros/json_diagnostics/ "
            "This macro enables extended diagnostics for exception messages."
        )
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "json_diagnostics": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/[>=3.11 <3.13]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["JSON_VALIDATOR_BUILD_TESTS"] = False
        tc.cache_variables["JSON_VALIDATOR_BUILD_EXAMPLES"] = False
        tc.cache_variables["JSON_VALIDATOR_INSTALL"] = True
        tc.cache_variables["JSON_VALIDATOR_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["CMAKE_INSTALL_RUNTIMEDIR"] = "bin"
        if self.options.json_diagnostics:
            tc.preprocessor_definitions["JSON_DIAGNOSTICS"] = '1'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nlohmann_json_schema_validator")
        self.cpp_info.set_property("cmake_target_name", "nlohmann_json_schema_validator::validator")
        # Upstream changed the target name in a minor release, keep an alias for compatibility on the conan side
        self.cpp_info.set_property("cmake_target_aliases", ["nlohmann_json_schema_validator"])
        self.cpp_info.libs = ["nlohmann_json_schema_validator"]
        if self.options.json_diagnostics:
            self.cpp_info.defines = ["JSON_DIAGNOSTICS=1"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("JSON_SCHEMA_VALIDATOR_EXPORTS=1")

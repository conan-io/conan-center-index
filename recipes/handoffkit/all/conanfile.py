from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os

required_conan_version = ">=2.0.9"


class HandoffkitConan(ConanFile):
    name = "handoffkit"
    description = "Native C++20 multi-agent runtime with structured handoffs"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DaosPath/handoffkit"
    topics = ("multi-agent", "handoffs", "llm", "runtime")
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
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Public headers include <nlohmann/json.hpp>
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["HANDOFFKIT_BUILD_TESTS"] = False
        tc.cache_variables["HANDOFFKIT_BUILD_EXAMPLES"] = False
        tc.cache_variables["HANDOFFKIT_BUILD_CLI"] = False
        # Package the runtime core only (no fusion demo suite / CLI catalog).
        tc.cache_variables["HANDOFFKIT_BUILD_DEMOS"] = False
        tc.cache_variables["HANDOFFKIT_FETCH_JSON"] = False
        tc.cache_variables["HANDOFFKIT_WITH_HTTP"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "handoffkit")
        self.cpp_info.set_property("cmake_target_name", "handoffkit::handoffkit")
        # Alias used by monorepo docs / consumer_core example
        self.cpp_info.set_property("cmake_target_aliases", ["handoffkit::core"])
        self.cpp_info.libs = ["handoffkit_core"]
        self.cpp_info.requires = ["nlohmann_json::nlohmann_json"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m"])

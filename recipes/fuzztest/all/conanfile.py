from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, save
import os
import yaml

required_conan_version = ">=1.53.0"


class FuzztestConan(ConanFile):
    name = "fuzztest"
    description = "A C++ testing framework for writing and executing fuzz tests"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/fuzztest"
    topics = ("fuzzing", "testing")
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

    @property
    def _min_cppstd(self):
        return 17

    def export(self):
        copy(self, f"_package_info-{self.version}.yml",
             os.path.join(self.recipe_folder, "package_info"),
             os.path.join(self.export_folder))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/20240116.1@local/beta", transitive_headers=True, force=True) # Waiting on PR
        self.requires("antlr4-cppruntime/4.13.1")
        # TODO: Maybe an option to disable GTest? In case user wants to use another testing framework
        self.requires("gtest/1.14.0", transitive_headers=True)
        self.requires("re2/20240301@local/beta", transitive_headers=True, force=True) # Waiting on PR, uses internal headers

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        # https://github.com/google/fuzztest/blob/main/doc/quickstart-cmake.md#prerequisites
        # Clang (with libc++) verifed working as far back as clang 12.
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Clang")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _fetchcontent_to_findpackage(self):
        # Replace the entirety of the FetchContent-based dependency fetching with find_packages
        save(self, os.path.join(self.source_folder, "cmake", "BuildDependencies.cmake"), """
find_package(re2 REQUIRED CONFIG)
find_package(absl REQUIRED CONFIG)
find_package(GTest REQUIRED CONFIG)
find_package(antlr4-runtime REQUIRED CONFIG)
""")

    def build(self):
        self._fetchcontent_to_findpackage()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "fuzztest"),
             os.path.join(self.package_folder, "include", "fuzztest"))
        for ext in (".so", ".lib", ".a", ".dylib", ".bc"):
            copy(self, f"*{ext}", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)

        copy(self, "AddFuzzTest.cmake", os.path.join(self.source_folder, "cmake"), os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "FuzzTestFlagSetup.cmake", os.path.join(self.source_folder, "cmake"), os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        info_path = os.path.join(self.recipe_folder, f"_package_info-{self.version}.yml")
        info = yaml.safe_load(open(info_path, "r"))

        # Fuzztest does not document a way to consume with find_package, so stick with the default name.

        # For functions like fuzztest_setup_fuzzing_flags()
        self.cpp_info.set_property("cmake_build_modules", [
            os.path.join("lib", "cmake", "AddFuzzTest.cmake"),
            os.path.join("lib", "cmake", "FuzzTestFlagSetup.cmake"),
        ])

        # TODO: Used, but not linked to anything?
        self.cpp_info.components["_hidden"].requires = ["antlr4-cppruntime::antlr4-cppruntime"]
        self.cpp_info.components["_hidden"].libdirs = []
        self.cpp_info.components["_hidden"].includedirs = []

        for name, data in info.items():
            component = self.cpp_info.components[name]
            if not data["header_only"]:
                component.libs = [f"fuzztest_{name}"]
                component.requires = data["deps"]
            else:
                component.libdirs = []

# type: ignore
from pathlib import Path
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, save, copy
import os
import yaml

required_conan_version = ">=2.0.0"

class FuzztestConan(ConanFile):    
    name = "fuzztest"
    version = 'cci.20250728'
    description = "A C++ testing framework for writing and executing fuzz tests"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/fuzztest"
    topics = ("fuzzing", "testing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        'with_flatbuffers': [True, False],
        "fuzzing": ['', 'libfuzzer'],
        "compatibility": [True, False]
    }
    default_options = {
        "with_flatbuffers": False,
        "fuzzing": '',
        "compatibility": False,
    }
    
    
    @property
    def _min_cppstd(self):
        return 17
    
    def layout(self):
        cmake_layout(self)
    
    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        # https://github.com/google/fuzztest/blob/main/doc/quickstart-cmake.md#prerequisites
        # Clang (with libc++) verifed working as far back as clang 12.
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Clang")
        
    def requirements(self):
        self.requires('abseil/20240116.1')
        self.requires('re2/20251105')
        self.requires('gtest/1.17.0')
        self.requires('antlr4-cppruntime/4.13.2')
        if self.options.with_flatbuffers:
            self.requires('flatbuffers/25.9.23')
            
        self.build_requires("cmake/3.31.9")
        
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()
        
    def _patch_sources(self):
        save(self, Path(self.source_folder) / 'cmake' / 'BuildDependencies.cmake', """
            find_package(absl REQUIRED)
            find_package(re2 REQUIRED)
            find_package(gtest REQUIRED)
            find_package(antlr-cpp REQUIRED)
            if(FUZZTEST_BUILD_FLATBUFFERS)
                find_package(flatbuffers REQUIRED)
            endif()
            """
        )
        
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['FUZZTEST_BUILD_TESTING'] = False
        tc.variables['FUZZTEST_FUZZING_MODE'] = self.options.fuzzing
        tc.variables['FUZZTEST_COMPATIBILITY_MODE'] = self.options.compatibility_mode
        tc.variables['FUZZTEST_BUILD_FLATBUFFERS'] = self.options.with_flatbuffers
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        
    def build(self):
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

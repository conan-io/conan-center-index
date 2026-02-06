from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"

class GustaveRecipe(ConanFile):
    name = "gustave"
    description = "A structural integrity library for video games"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vsaulue/Gustave"
    topics = ("physics", "structural-integrity", "game-development", "header-library")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.29 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["CMAKE_COMPILE_WARNING_AS_ERROR"] = False
        tc.cache_variables["GUSTAVE_BUILD_DOCS"] = False
        tc.cache_variables["GUSTAVE_BUILD_TOOLS"] = False
        tc.cache_variables["GUSTAVE_BUILD_TUTORIALS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=str(self.recipe_folder), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install(component="Distrib-Std")

    def package_info(self):
        std = self.cpp_info.components['distrib-std']
        std.libdirs = []
        std.bindirs = []
        std.includedirs = ['distrib-std/include']
        std.set_property('cmake_file_name', 'Gustave')
        std.set_property('cmake_target_name', 'Gustave::Distrib-Std')

        # Disable the generation of the default 'gustave::gustave' target by giving it an existing name.
        self.cpp_info.set_property('cmake_file_name', 'Gustave')
        self.cpp_info.set_property('cmake_target_name', 'Gustave::Distrib-Std')

    def package_id(self):
        self.info.clear()

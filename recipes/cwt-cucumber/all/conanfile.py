import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class CwtCucumberRecipe(ConanFile):
    name = "cwt-cucumber"
    license = "MIT"
    homepage = "https://github.com/ThoSe1990/cucumber-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C++20 Cucumber interpreter"
    topics = ("cpp", "bdd", "testing", "cucumber")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    implements = ["auto_shared_fpic"]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.os == "Windows":
            # No explicit support for shared libraries on Windows
            self.options.rm_safe("shared")
            self.package_type = "static-library"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("nlohmann_json/[~3.11]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def validate(self):
        check_min_cppstd(self, 20)
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "15":
            raise ConanInvalidConfiguration(f"std::format support requires Apple Clang 15.0 or higher.")

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "13":
            raise ConanInvalidConfiguration(f"std::format support requires GCC 13 or higher.")

    def generate(self):
        tc = CMakeToolchain(self)
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

    def package_info(self):
        self.cpp_info.components["cucumber"].set_property("cmake_target_name", "cwt::cucumber")
        self.cpp_info.components["cucumber"].libs = ["cucumber"]

        self.cpp_info.components["cucumber-no-main"].set_property("cmake_target_name", "cwt::cucumber-no-main")
        self.cpp_info.components["cucumber-no-main"].libs = ["cucumber-no-main"]

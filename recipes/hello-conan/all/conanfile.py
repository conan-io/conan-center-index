from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import save

from pathlib import Path

required_conan_version = ">=2.12"

class hello_conanRecipe(ConanFile):
    name = "hello-conan"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Dummy recipe for internal testing"
    topics = ("conan-testing", "dummy")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # save a dummy .la file to trigger hook warning
        la_file = Path(self.package_folder) / "lib" / "hello-conan-foobar.la"
        save(self, la_file.as_posix(), "foobar")

    def package_info(self):
        self.cpp_info.libs = ["hello-conan"]


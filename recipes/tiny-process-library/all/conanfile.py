import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import rmdir, copy, get, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=2.1"


class tinyProcessRecipe(ConanFile):
    name = "tiny-process-library"

    # Optional metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/eidheim/tiny-process-library"
    description = "A small platform independent library making it simple to create and stop new processes in C++, as well as writing to stdin and reading from stdout and stderr of a new process."
    topics = ("process", "subprocess")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    package_type = "library"

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("tiny-process-library does not support shared libraries on Windows")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"  # CMake 4 support
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["tiny-process-library"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")


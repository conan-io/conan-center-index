from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import collect_libs, get, copy, rmdir, replace_in_file
import os

required_conan_version = ">=2.1"

class PmpConan(ConanFile):
    name = "pmp"
    license = "MIT"
    url = "https://github.com/pmp-library/pmp-library"
    description = "PMP library - a library for processing polygon meshes."
    topics = ("geometry", "mesh processing", "3D", "polygon mesh")
    package_type = "library"

    # Binary configuration
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

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD",
                        "#set(CMAKE_CXX_STANDARD")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # TODO: Check if VIS tools would be useful in the future
        tc.cache_variables["PMP_BUILD_VIS"] = False
        tc.cache_variables["PMP_BUILD_EXAMPLES"] = False
        tc.cache_variables["PMP_BUILD_TESTS"] = False
        tc.cache_variables["PMP_BUILD_DOCS"] = False
        tc.cache_variables["PMP_BUILD_REGRESSIONS"] = False
        tc.cache_variables["PMP_STRICT_COMPILATION"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder)

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pmp")
        self.cpp_info.set_property("cmake_target_name", "pmp::pmp")
        self.cpp_info.set_property("pkg_config_name", "pmp")
        self.cpp_info.libs = ["pmp"]

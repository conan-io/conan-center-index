from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, collect_libs
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class HppFclConan(ConanFile):
    name = "hpp-fcl"
    description = "An extension of the Flexible Collision Library"
    license = "BSD-3-Clause"
    homepage = "https://github.com/humanoid-path-planner/hpp-fcl"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_py_interface": [True, False],
        "install_documentation": [True, False],
        "turn_assert_into_exception": [True, False],
        "enable_logging": [True, False],
        "has_qhull": [True, False],
        "has_octomap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_py_interface": False,
        "install_documentation": False,
        "turn_assert_into_exception": False,
        "enable_logging": False,
        "has_qhull": False,
        "has_octomap": False
    }

    def requirements(self):
        self.requires("eigen/[>=3.4.0]", package_id_mode="minor_mode")
        self.requires("boost/1.76.0")
        self.requires("assimp/5.4.1")
        if self.options.has_octomap:
            self.requires("octomap/1.10.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_PYTHON_INTERFACE"] = self.options.with_py_interface
        tc.variables["INSTALL_DOCUMENTATION"] = self.options.install_documentation
        tc.variables["HPP_FCL_ENABLE_LOGGING"] = self.options.enable_logging
        tc.variables["HPP_FCL_HAS_OCTOMAP"] = self.options.has_octomap
        tc.variables["HPP_FCL_HAS_QHULL"] = self.options.has_qhull
        if Version(self.version) >= "2.4.5":
            tc.variables["HPP_FCL_TURN_ASSERT_INTO_EXCEPTION"] = self.options.turn_assert_into_exception
        else:
            del self.options.turn_assert_into_exception
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.set_property("cmake_file_name", "hpp-fcl")
        self.cpp_info.set_property("cmake_target_name", "hpp-fcl::hpp-fcl")
        self.cpp_info.set_property("pkg_config_name", "hpp-fcl")
        self.cpp_info.libs = collect_libs(self)

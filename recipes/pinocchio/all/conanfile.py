import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, rmdir, copy

required_conan_version = ">=2"

class PinocchioConan(ConanFile):
    name = "pinocchio"
    package_type = "shared-library"
    license = ("BSD-2-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://stack-of-tasks.github.io/pinocchio/"
    description = "A fast and flexible implementation of Rigid Body Dynamics algorithms and their analytical derivatives"
    topics = (
        "robotics", "kinematics", "dynamics", "automatic-differentiation",
        "motion-planning", "ros", "rigid-body-dynamics", "analytical-derivatives",
        )

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_collision_support": [True, False]
    }
    default_options = {
        "with_collision_support": False
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/[>=3.4.0 <4]", transitive_headers=True)
        self.requires("urdfdom_headers/1.1.1")
        self.requires("urdfdom/4.0.0", transitive_headers=True)
        self.requires("boost/[>=1.84.0 <1.90.0]", transitive_headers=True)
        if self.options.with_collision_support:
            self.requires("coal/[~3.0.1]")
          
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_PYTHON_INTERFACE"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_WITH_COLLISION_SUPPORT"] = self.options.with_collision_support
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.generate()

        deps = CMakeDeps(self)
        # coal is a fork/continuation of hpp-fcl, pinocchio still uses hpp-fcl names,
        # but coal provides compatibility headers if the target links against the coal library
        deps.set_property("coal", "cmake_file_name", "hpp-fcl")
        deps.set_property("coal", "cmake_target_name", "hpp-fcl::hpp-fcl")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["pinocchio_headers"].includedirs = ["include"]
        self.cpp_info.components["pinocchio_headers"].requires = ["eigen::eigen", "boost::boost"]
        self.cpp_info.components["pinocchio_headers"].libdirs = []

        self.cpp_info.components["pinocchio_default"].libs = ["pinocchio_default"]
        self.cpp_info.components["pinocchio_default"].requires = ["pinocchio_headers"]
        self.cpp_info.components["pinocchio_default"].set_property("cmake_target_name", "pinocchio::pinocchio_default")
        self.cpp_info.components["pinocchio_default"].defines = ["PINOCCHIO_ENABLE_TEMPLATE_INSTANTIATION"]

        self.cpp_info.components["pinocchio_visualizers"].libs = ["pinocchio_visualizers"]
        self.cpp_info.components["pinocchio_visualizers"].requires = ["pinocchio_headers", "pinocchio_default"]
        self.cpp_info.components["pinocchio_visualizers"].set_property("cmake_target_name", "pinocchio::pinocchio_visualizers")

        self.cpp_info.components["pinocchio_parsers"].libs = ["pinocchio_parsers"]
        self.cpp_info.components["pinocchio_parsers"].set_property("cmake_target_name", "pinocchio::pinocchio_parsers")
        self.cpp_info.components["pinocchio_parsers"].requires = ["pinocchio_headers", "pinocchio_default", "boost::headers", "urdfdom::urdfdom", "urdfdom_headers::urdfdom_headers"]
        self.cpp_info.components["pinocchio_parsers"].defines = ["PINOCCHIO_WITH_URDFDOM"]

        self.cpp_info.components["pinocchio"].requires = ["pinocchio_default", "pinocchio_parsers", "pinocchio_visualizers"]
        self.cpp_info.components["pinocchio"].set_property("cmake_target_name", "pinocchio::pinocchio")

        if self.options.with_collision_support:
            self.cpp_info.components["pinocchio_collision"].libs = ["pinocchio_collision"]
            self.cpp_info.components["pinocchio_collision"].requires = ["pinocchio_headers", "pinocchio_default", "coal::coal"]
            self.cpp_info.components["pinocchio_collision"].set_property("cmake_target_name", "pinocchio::pinocchio_collision")
            self.cpp_info.components["pinocchio_parsers"].requires.append("pinocchio_collision")
            self.cpp_info.components["pinocchio"].requires.append("pinocchio_collision")
            for comp_name in ["pinocchio_headers", "pinocchio_default", "pinocchio_visualizers", "pinocchio_parsers", "pinocchio"]:
                self.cpp_info.components[comp_name].requires.append("coal::coal")
                self.cpp_info.components[comp_name].defines.append("PINOCCHIO_WITH_HPP_FCL")

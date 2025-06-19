import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, rmdir, copy

required_conan_version = ">=2"

class PinocchioConan(ConanFile):
    name = "pinocchio"
    package_type = "library"
    license = ("BSD 2-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "Pinocchio instantiates the state-of-the-art Rigid Body Algorithms for poly-articulated "
        "systems based on revisited Roy Featherstone's algorithms. Besides, Pinocchio provides "
        "the analytical derivatives of the main Rigid-Body Algorithms, such as the Recursive "
        "Newton-Euler Algorithm or the Articulated-Body Algorithm."
        )
    topics = (
        "robotics", "kinematics", "dynamics", "automatic-differentiation",
        "motion-planning", "ros", "rigid-body-dynamics", "analytical-derivatives",
        )

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True
        }
    
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("urdfdom_headers/1.1.1")
        self.requires("urdfdom/4.0.0")
        self.requires("boost/1.87.0", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")

    def validate(self):
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("MSVC is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # To enable building Python interfaces, it is necessary to either ensure the installation
        # of dependencies using self.tool_requires("cpython/X.Y.Z") or implement support for working
        # with a virtual environment (e.g., https://github.com/conan-io/conan/pull/11601)
        tc.cache_variables["BUILD_PYTHON_INTERFACE"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

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

    def package_info(self):
        self.cpp_info.libs = ["pinocchio_default", "pinocchio_parsers", "pinocchio_visualizers"]

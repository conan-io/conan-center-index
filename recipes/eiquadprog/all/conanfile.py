from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get


class EiquadprogConan(ConanFile):
    name = "eiquadprog"
    package_type = "library"

    license = ("LGPL-3.0", "GPL-3.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stack-of-tasks/eiquadprog"
    description = (
        "This package contains different C++ implementations of the algorithm of Goldfarb and "
        "Idnani for the solution of a (convex) Quadratic Programming problem by means of a dual method."
    )

    topics = ("algebra", "math", "robotics", "optimization", "quadratic-programming")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tests": [True, False],
    }
    default_options = {"shared": False, "fPIC": True, "build_tests": False}

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.build_tests:
            self.requires("boost/1.87.0", options={"shared": True})

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        if not self.options.build_tests:
            tc.variables["BUILD_TESTING"] = "OFF"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["eiquadprog"]

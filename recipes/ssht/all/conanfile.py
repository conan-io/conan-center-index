from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class SshtConan(ConanFile):
    name = "ssht"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astro-informatics/ssht"
    description = "Fast spin spherical harmonic transforms"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("physics", "astrophysics", "radio interferometry")
    package_type = "static-library"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fftw/3.3.10")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("SSHT requires C99 support for complex numbers.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["tests"] = False
        tc.cache_variables["python"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("fftw", "cmake_target_name", "FFTW3::FFTW3")
        deps.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["ssht"]

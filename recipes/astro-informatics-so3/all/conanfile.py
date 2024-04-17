import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class AstroInformaticsSO3(ConanFile):
    name = "astro-informatics-so3"
    description = "Fast and accurate Wigner transforms"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astro-informatics/so3"
    topics = ("physics", "astrophysics", "radio interferometry")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("ssht/1.5.2", transitive_headers=True, transitive_libs=True)
        self.requires("fftw/3.3.10")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(
                "Visual Studio not supported, since SO3 requires C99 support for complex numbers"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["conan_deps"] = False
        tc.variables["CONAN_EXPORTED"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("fftw", "cmake_target_name", "FFTW3::FFTW3")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["astro-informatics-so3"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from os.path import join

required_conan_version = ">=2"


class ScipPlusPlus(ConanFile):
    name = "scippp"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"
    description = "SCIP++ is a C++ wrapper for SCIP's C interface"
    package_type = "library"
    topics = ("mip", "solver", "linear", "programming")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/scipopt/SCIPpp"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def validate(self):
        check_min_cppstd(self, 17)
        check_min_vs(self, 192)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        # see https://github.com/scipopt/SCIPpp/blob/1.0.0/conanfile.py#L25
        self.requires(f"scip/{self.conan_data['scip_mapping'][self.version]}", transitive_headers=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # In upstream, the version is injected into CMake via git.
        tc.variables["scippp_version"] = self.version
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ScipPP"]

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from os.path import join


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

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        # see https://github.com/scipopt/SCIPpp/commit/faa80e753f96094004467c1daa98a7ab4d86f279
        if Version(self.version) >= "1.1.0":
            return {
                "gcc": "8",
                "clang": "7",
                "apple-clang": "11",
                "msvc": "192"
            }
        else:
            return {
                "gcc": "7",
                "clang": "7",
                "apple-clang": "10",
                "msvc": "192"
            }

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

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
        self.requires("scip/8.0.4", transitive_headers=True)

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

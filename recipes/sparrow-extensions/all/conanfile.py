from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class SparrowExtensionsRecipe(ConanFile):
    name = "sparrow-extensions"
    description = "Apache Arrow canonical extensions for Sparrow"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/QuantStack/sparrow-extensions"
    topics = ("arrow", "apache arrow", "extensions", "uuid", "json", "boolean", "sparrow")
    package_type = "library"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        # Note: sparrow-extensions 0.2.0 was developed against sparrow 2.0.0,
        # but we use 1.4.0 as it's the latest available in conan-center-index
        self.requires("sparrow/[>=1.4.0 <2]", transitive_headers=True, transitive_libs=True)

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "16",
            "clang": "18",
            "gcc": "11.2",
            "msvc": "194",
        }

    def validate(self):
        check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < Version(minimum_version):
            raise ConanInvalidConfiguration(f"{self.name} requires {self.settings.compiler} {minimum_version} or newer")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.28]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPARROW_EXTENSIONS_BUILD_SHARED"] = self.options.shared
        tc.variables["SPARROW_EXTENSIONS_BUILD_TESTS"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["SPARROW_EXTENSIONS_BUILD_DOCS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["ENABLE_INTEGRATION_TEST"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share", "cmake"))

    def package_info(self):
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.set_property("cmake_file_name", "sparrow-extensions")
        self.cpp_info.set_property("cmake_target_name", "sparrow-extensions::sparrow-extensions")
        self.cpp_info.libs = [f"sparrow-extensions{postfix}"]
        
        if not self.options.shared:
            self.cpp_info.defines.append("SPARROW_EXTENSIONS_STATIC_LIB")

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class SparrowRecipe(ConanFile):
    name = "sparrow"
    description = "C++20 idiomatic APIs for the Apache Arrow Columnar Format"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/man-group/sparrow"
    topics = ("arrow", "apache arrow", "columnar format", "dataframe")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_date_polyfill": [True, False],
    }
    default_options = {"shared": False, "fPIC": True, "use_date_polyfill": False}

    def requirements(self):
        if self.options.use_date_polyfill:
            self.requires("date/3.0.3")

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {"apple-clang": "16", "clang": "18", "gcc": "12", "msvc": "194"}

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder=".")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_DATE_POLYFILL"] = self.options.use_date_polyfill
        if is_msvc(self):
            tc.variables["USE_LARGE_INT_PLACEHOLDERS"] = True
        tc.generate()

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

    def package_info(self):
        defines = []
        if self.options.use_date_polyfill:
            defines.append("SPARROW_USE_DATE_POLYFILL")
        if is_msvc(self):
            defines.append("SPARROW_USE_LARGE_INT_PLACEHOLDERS")

        self.cpp_info.libs = ["sparrow"]
        self.cpp_info.defines = defines
        self.cpp_info.set_property("cmake_file_name", "sparrow")
        self.cpp_info.set_property("cmake_target_name", "sparrow::sparrow")

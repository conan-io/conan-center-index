from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class NepdateConan(ConanFile):
    name = "nepdate"
    description = ("Bikram Sambat (Nepali calendar) dates for C++20: BS to AD conversion, arithmetic, "
                   "fiscal year, formatting and parsing, plus the optional patro library for tithi, "
                   "public holidays and events")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sanamhub/nepdate-cpp"
    topics = ("nepali", "calendar", "bikram-sambat", "date", "patro", "tithi")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_patro": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_patro": True,
    }
    options_description = {
        "enable_patro": "Build the compiled nepdate::patro library; when False the package is the header-only core",
    }
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        # The oldest compilers upstream builds and tests (CHANGELOG.md of 0.1.0-beta.1)
        return {
            "apple-clang": "16",
            "clang": "16",
            "gcc": "12",
            "msvc": "194",
        }

    def configure(self):
        if not self.options.enable_patro:
            self.options.rm_safe("shared")
            self.options.rm_safe("fPIC")
            self.package_type = "header-library"
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if not self.info.options.enable_patro:
            self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        if self.options.enable_patro:
            self.tool_requires("cmake/[>=3.25 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.enable_patro:
            tc = CMakeToolchain(self)
            tc.cache_variables["NEPDATE_BUILD_PATRO"] = True
            tc.cache_variables["NEPDATE_BUILD_TESTS"] = False
            tc.cache_variables["NEPDATE_BUILD_TOOLS"] = False
            tc.generate()

    def build(self):
        if self.options.enable_patro:
            cmake = CMake(self)
            cmake.configure()
            # Only the library: the top-level project also adds an internal check program (tools/coreonly)
            cmake.build(target="nepdate_patro")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "THIRD-PARTY-NOTICES.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.options.enable_patro:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rm(self, "*.pdb", self.package_folder, recursive=True)
        else:
            copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nepdate")

        self.cpp_info.components["nepdate"].set_property("cmake_target_name", "nepdate::nepdate")
        self.cpp_info.components["nepdate"].bindirs = []
        self.cpp_info.components["nepdate"].libdirs = []

        if self.options.enable_patro:
            self.cpp_info.components["patro"].set_property("cmake_target_name", "nepdate::patro")
            self.cpp_info.components["patro"].libs = ["nepdate_patro"]
            self.cpp_info.components["patro"].requires = ["nepdate"]

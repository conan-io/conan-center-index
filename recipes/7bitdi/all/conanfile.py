from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class SevenBitDIConan(ConanFile):
    name = "7bitdi"
    homepage = "https://github.com/7bitcoder/7bitDI"
    description = "7bitDI is a simple C++ dependency injection library."
    topics = ("cpp17", "dependency-injector", "injector", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "msvc": "192",
            "gcc": "6",
            "clang": "6",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.get_safe("shared") or self.options.header_only:
            self.options.rm_safe("fPIC")
        if self.options.header_only:
            self.options.rm_safe("shared")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        compiler = self.settings.compiler
        compiler_name = str(compiler)

        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        minimum_version = self._minimum_compilers_version.get(compiler_name, False)
        if minimum_version and Version(compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"Requires compiler {compiler_name} minimum version: {minimum_version} with C++17 support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["_7BIT_DI_BUILD_EXAMPLES"] = False
            tc.variables["_7BIT_DI_BUILD_TESTS"] = False
            tc.variables["_7BIT_DI_BUILD_DOC"] = False
            tc.variables["_7BIT_DI_BUILD_SINGLE_HEADER"] = False
            tc.variables["_7BIT_DI_INSTALL"] = True
            tc.variables["_7BIT_DI_LIBRARY_TYPE"] = self.getSevenBitDILibraryType()
            tc.generate()

    def getSevenBitDILibraryType(self):
        if self.options.header_only:
            return "HeaderOnly"
        elif self.options.shared:
            return "Shared"
        else:
            return "Static"

    def build(self):
        if not self.options.header_only:
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
        if self.options.header_only:
            copy(
                self,
                src=os.path.join(self.source_folder, "Include"),
                pattern="*.hpp",
                dst=os.path.join(self.package_folder, "include"),
            )
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "7bitDI")
        self.cpp_info.set_property("cmake_target_name", "7bitDI::7bitDI")

        if self.options.header_only:
            self.cpp_info.libs = []
            self.cpp_info.bindirs = []
        else:
            suffix = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = ["7bitDI" + suffix]

            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "7bitDI"
        self.cpp_info.names["cmake_find_package_multi"] = "7bitDI"

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class Md4QtConan(ConanFile):
    name = "md4qt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/md4qt"
    license = "MIT"
    description = "C++ library for parsing Markdown."
    topics = ("markdown", "gfm", "parser", "ast", "commonmark", "md", "qt6", "cpp17")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def configure(self):
        if Version(self.version) < "5.0.0":
            self.package_type = "header-library"
        else:
            self.package_type = "static-library"

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "191",
            "gcc": "9",
            "clang": "12",
            "apple-clang": "14",
        }

    def layout(self):
        if Version(self.version) < "5.0.0":
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "5.0.0":
            self.requires("icu/74.2")
            self.requires("uriparser/0.9.7")
        else:
            self.requires("qt/6.8.3", options={
                "gui": False,
                "widgets": False,
                "with_pq": False,
                "with_odbc": False,
                "with_sqlite3": False
            })
            self.requires("extra-cmake-modules/6.8.0")

    def generate(self):
        if Version(self.version) >= "5.0.0":
            tc = CMakeToolchain(self)
            tc.cache_variables["BUILD_MD4QT_TESTS"] = False
            tc.generate()

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        if Version(self.version) >= "5.0.0":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        if Version(self.version) <= "2.8.1":
            copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        else:
            copy(self, "MIT.txt", src=os.path.join(self.source_folder, "LICENSES"), dst=os.path.join(self.package_folder, "licenses"))
        if Version(self.version) < "4.0.0":
            copy(self, "*.hpp", src=os.path.join(self.source_folder, "md4qt"), dst=os.path.join(self.package_folder, "include", "md4qt"))
        elif Version(self.version) < "5.0.0":
            copy(self, "*.h", src=os.path.join(self.source_folder, "md4qt"), dst=os.path.join(self.package_folder, "include", "md4qt"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "md4qt")
        self.cpp_info.set_property("cmake_target_name", "md4qt::md4qt")
        if Version(self.version) >= "5.0.0":
            self.cpp_info.libs = ["md4qt"]
        else:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []

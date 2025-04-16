from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

class PackageConan(ConanFile):
    name = "qtils"
    version = "0.0.4"
    description = "Utils for KAGOME C++ projects"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qdrvm/qtils"
    topics = ("KAGOME", "header-only")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    options = {}
    default_options = {}
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "11",
            "clang": "10",
            "gcc": "10",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.84.0", transitive_headers=True)
        self.requires("fmt/10.1.1", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                f"{self.ref} can not be used on Windows due to platform-specific dependencies."
            )
        
        if self.dependencies["boost"].ref.version < "1.74.0":
            raise ConanInvalidConfiguration(
                f"{self.ref} requires Boost >= 1.74.0"
            )
        
        if self.dependencies["fmt"].ref.version < "8.0.0":
            raise ConanInvalidConfiguration(
                f"{self.ref} requires fmt >= 8.0.0"
            )
        
        if self.settings.compiler.get_safe("cppstd") and \
           Version(str(self.settings.compiler.cppstd)) < "20":
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++20 or higher for std::span and concepts support"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "src"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "qtils")
        self.cpp_info.set_property("cmake_target_name", "qtils::qtils")
        self.cpp_info.set_property("pkg_config_name", "qtils")

        self.cpp_info.defines = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        self.cpp_info.filenames["cmake_find_package"] = "qtils"
        self.cpp_info.filenames["cmake_find_package_multi"] = "qtils"
        self.cpp_info.names["cmake_find_package"] = "qtils"
        self.cpp_info.names["cmake_find_package_multi"] = "qtils"

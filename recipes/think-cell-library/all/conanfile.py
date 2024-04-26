from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "think-cell-library"
    description = "This library consists of several core C++ utilities that we at think-cell Software have developed and consider to be useful."
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case it's not listed there, use "LicenseRef-<license-file-name>"
    license = "BSL-1.0 license"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/think-cell/think-cell-library"
    # Do not put "conan" nor the project name in topics. Use topics from the upstream listed on GH
    # Keep 'header-only' as topic
    topics = ("ranges",  "header-only")
    package_type = "header-library"
    # Keep these or explain why it's not required for this particular case
    settings = "os", "arch", "compiler", "build_type"
    # Do not copy sources to build folder for header only projects, unless you need to apply patches
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    # In case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "13",
            "clang": "7",
            "gcc": "12",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def layout(self):
        # src_folder must use the same source folder name than the project
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Prefer self.requires method instead of requires attribute
        # Direct dependencies of header only libs are always transitive since they are included in public headers
        self.requires("boost/1.83.0")

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # Validate the minimum cpp standard supported when installing the package. For C++ projects only
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        # In case this library does not work in some another configuration, it should be validated here too
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can not be used on Windows.")

    def source(self):
        # Download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    # Not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        pass

    # Copy all files to the package folder
    def package(self):
        copy(self, "LICENSE_1_0.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "tc"),
            os.path.join(self.package_folder, "include", "tc"),
        )

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

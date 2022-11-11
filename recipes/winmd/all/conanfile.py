import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.52.0"


class WinMDConan(ConanFile):
    name = "winmd"
    description = "C++ winmd parser"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "LicenseRef-<license-file-name>"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/winmd"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    # Keep 'hearder-only' as topic
    topics = ("native", "C++", "WinRT", "WinMD")
    settings = "os", "arch", "compiler", "build_type"  # even for header only
    no_copy_source = True  # do not copy sources to build folder for header only projects, unless, need to apply patches

    @property
    def _min_cppstd(self):
        return 17

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self, src_folder="src")

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        # FIXME: `self.settings` is not available in 2.0 but there are plenty of open issues about
        # the migration point. For now we are only going to write valid 1.x recipes until we have a proper answer
        if self.settings.compiler.get_safe("cppstd"):
            # validate the minimum cpp standard supported when installing the package. For C++ projects only
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        # download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    # copy all files to the package folder
    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "src"),
        )

    def package_info(self):
        if not is_msvc(self):
            # ignore shadowing errors
            self.cpp_info.cppflags = ['-fpermissive']

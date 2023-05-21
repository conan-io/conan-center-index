from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class ChefFunConan(ConanFile):
    name = "chef-fun"
    homepage = "https://gitlab.com/libchef/chef-fun"
    description = "C++ Functional programming support library"
    topics = ("functional programming", "cpp", "library" )
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    # Keep these or explain why it's not required for this particular case
    # Do not copy sources to build folder for header only projects, unless you need to apply patches
    no_copy_source = True
    version = "1.0.1"
    generators = "cmake"

    @property
    def _min_cppstd(self):
        return 20

    # In case the project requires C++14/17/20/... the minimum compiler version should be listed
    # Not tested on "msvc", "clang", and "apple-clang". Possibly it works there
    # given a sufficient recent version
    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9.4.0",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

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

    #
    def source(self):
        self.run("git clone --depth 1 --branch 1.0.1 https://gitlab.com/libchef/chef-fun.git")

    # Copy all files to the package folder
    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hh",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )
        copy(
            self,
            pattern="*.tcc",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="chef-fun")
        cmake.build()
        cmake.test()

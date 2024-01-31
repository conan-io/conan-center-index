from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class StduuidConan(ConanFile):
    name = "stduuid"
    description = "A C++17 cross-platform implementation for UUIDs"
    topics = ("uuid", "guid", "header-only")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mariusbancila/stduuid"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        # True: Use std::span
        # False: Use gsl::span
        "with_cxx20_span": [True, False],
    }

    @property
    def _min_cppstd(self):
        return "20" if self.options.get_safe("with_cxx20_span") else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "5",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }
    
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def config_options(self):
        if Version(self.version) == "1.0":
            # Version 1.0 unconditionally depends on gsl span
            del self.options.with_cxx20_span
        else:
            # Conditionally set the default value of with_cxx20_span
            # if cppstd is set and is 20 or greater
            self.options.with_cxx20_span = (self.settings.compiler.get_safe("cppstd", False)
                                            and valid_min_cppstd(self, 20))

    def requirements(self):
        if not self.options.get_safe("with_cxx20_span") or Version(self.version) == "1.0":
            self.requires("ms-gsl/4.0.0", transitive_headers=True)
        if self.settings.os == "Linux" and Version(self.version) <= "1.0":
            self.requires("util-linux-libuuid/2.39", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "uuid.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.get_safe("with_cxx20_span"):
            self.cpp_info.defines = ["LIBUUID_CPP20_OR_GREATER"]

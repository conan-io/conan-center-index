from conan import ConanFile
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.50.0"


class LibHALConan(ConanFile):
    name = "libhal"
    license = "Apache-2.0"
    description = ("A collection of interfaces and abstractions for embedded "
                   "peripherals and devices using modern C++")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libhal.github.io/"
    topics = ("peripherals", "hardware", "abstraction", "devices", "hal", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "Visual Studio": "17",
            "msvc": "193",
            "clang": "13",
            "apple-clang": "14"
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # NOTE: from the author, kammce, to the conan team. although boost-leaf
        # is marked as deprecated, it is required for libhal to work with bare
        # metal cross compilers such as the Arm GNU Toolchain. The main issue
        # with boost is its dependency on things such as bzip that cannot
        # compile on freestanding environments. boost-leaf has no dependencies
        # and can work in freestanding environments.
        version = Version(self.version)
        if "2.0.0" <= version and version < "3.0.0":
            self.requires("boost/1.83.0",
                          transitive_headers=True,
                          options={ "header_only": True })

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)
        minimum_version = self._compilers_minimum_version.get(compiler, False)
        if minimum_version and lazy_lt_semver(version, minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++{self._min_cppstd}, which your compiler ({compiler}-{version}) does not support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            "*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include")
        )
        copy(
            self,
            "*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include")
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

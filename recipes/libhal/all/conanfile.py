from conan import ConanFile
from conan.tools.files import get, copy
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

    @property
    def _bare_metal(self):
        return self.settings.os == "baremetal"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tl-function-ref/1.0.0")
        # NOTE from the author, kammce, and CCI maintainers:
        # although boost-leaf is deprecated, we've kept it for 2.x versions,
        # don't update it as upstream code won't work with boost itself
        self.requires("boost-leaf/1.81.0")

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
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler ({compiler}-{version}) does not support")


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self,
             "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses")
        )
        copy(self,
            "*.h",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include")
        )
        copy(self,
            "*.hpp",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include")
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        version = Version(self.version)
        if self._bare_metal and version < "3.0.0":
            self.cpp_info.defines = [
                "BOOST_LEAF_EMBEDDED",
                "BOOST_LEAF_NO_THREADS"
            ]

        # Note from CCI maintainers: Ensure users are aware of the deprecated
        # dependency
        if version < "3.0":
            self.output.warning(f"{self.name} < 3.0.0 uses boost-leaf which is a deprecated recipe. "
                                f"Once 3.0 is released, 2.x will also be deprecated.")

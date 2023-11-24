from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
)
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class LaudrupWinTLS(ConanFile):
    name = "laudrup-wintls"
    description = "Native Windows TLS stream wrapper for use with boost::asio"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wintls.dev"
    topics = (
        "header-only",
        "windows",
        "tls",
        "ssl",
        "networking",
        "boost",
        "asio",
        "sspi",
        "schannel",
    )
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = {}

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "clang": "12",
            "gcc": "7",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/[>=1.75 <2.0]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can only be used on Windows.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.set_property("cmake_target_name", "boost-wintls")
        self.cpp_info.filenames["cmake_find_package"] = "boost-wintls"
        self.cpp_info.filenames["cmake_find_package_multi"] = "boost-wintls"
        self.cpp_info.names["cmake_find_package"] = "boost-wintls"
        self.cpp_info.names["cmake_find_package_multi"] = "boost-wintls"

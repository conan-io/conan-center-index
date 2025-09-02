from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "sqlitemap"
    description = "sqlitemap - Persistent Map Backed by SQLite"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bw-hro/sqlitemap"
    topics = ("sqlite", "database", "hash map", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sqlite3/[>=3.45.0 <4]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sqlitemap")
        self.cpp_info.set_property("cmake_target_name", "sqlitemap::sqlitemap")
        self.cpp_info.set_property("pkg_config_name", "sqlitemap")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

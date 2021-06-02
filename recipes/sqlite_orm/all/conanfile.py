from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class SqliteOrmConan(ConanFile):
    name = "sqlite_orm"
    description = "SQLite ORM light header only library for modern C++."
    license = "BSD-3-Clause"
    topics = ("conan", "sqlite_orm", "sqlite", "sql", "database", "orm")
    homepage = "https://github.com/fnc12/sqlite_orm"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("sqlite_orm requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("sqlite_orm requires C++14, which your compiler does not support.")

    def requirements(self):
        self.requires("sqlite3/3.34.1")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "SqliteOrm"
        self.cpp_info.filenames["cmake_find_package_multi"] = "SqliteOrm"
        self.cpp_info.names["cmake_find_package"] = "sqlite_orm"
        self.cpp_info.names["cmake_find_package_multi"] = "sqlite_orm"

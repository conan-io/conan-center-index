from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class Sqlpp11Conan(ConanFile):
    name = "sqlpp11"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11"
    description = "A type safe SQL template library for C++"
    topics = ("sql", "dsl", "embedded", "data-base")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_stdcpp_version(self):
        return 11 if tools.scm.Version(self, self.version) < "0.61" else 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "10",
        }

    def requirements(self):
        self.requires("date/3.0.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, self._min_stdcpp_version)

        if self._min_stdcpp_version > 11:
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version:
                if tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration(f"{self.name} requires C++14, which your compiler does not support.")
            else:
                self.output.warn(f"{self.name} requires C++14. Your compiler is unknown. Assuming it supports C++14.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*", dst="bin", src=os.path.join(self._source_subfolder, "scripts"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Sqlpp11"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Sqlpp11"

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

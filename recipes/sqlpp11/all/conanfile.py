from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class Sqlpp11Conan(ConanFile):
    name = "sqlpp11"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11"
    description = "A type safe SQL template library for C++"
    topics = ("SQL", "DSL", "embedded", "data-base")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("date/3.0.1")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(
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

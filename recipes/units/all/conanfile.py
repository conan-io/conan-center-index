import os

from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version


class UnitsConan(ConanFile):
    name = "units"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nholthaus/units"
    description = "A compile-time, header-only, dimensional analysis and unit conversion library built on c++14 with no dependencies"
    topics = ("unit-conversion", "dimensional-analysis", "cpp14",
              "template-metaprogramming", "compile-time", "header-only",
              "no-dependencies")
    license = "MIT"
    no_copy_source = True
    settings = "compiler"

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, "14")
        minimum_version = {
            "clang": 3.4,
            "gcc": "4.9.3",
            "Visual Studio": 14.0,
        }.get(str(self.settings.compiler))
        if not minimum_version:
            self.output.warn(
                "Unknown compiler: assuming compiler supports C++14")
        else:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    "Compiler does not support C++14")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(
            "units.h",
            dst="include",
            src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

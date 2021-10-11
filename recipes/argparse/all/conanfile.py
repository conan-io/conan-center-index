from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class ArgparseConan(ConanFile):
    name = "argparse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/argparse"
    topics = ("argparse", "argument", "parsing")
    license = "MIT"
    description = "Argument Parser for Modern C++"
    settings = "compiler"
    no_copy_source = True

    _compiler_required_cpp17 = {
        "gcc": "7" if tools.Version(self.version) <= "2.1" else "8",
        "clang": "5" if tools.Version(self.version) <= "2.1" else "7",
        "Visual Studio": "15",
        "apple-clang": "10",
    }

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")
        try:
            minimum_required_compiler_version = self._compiler_required_cpp17[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if tools.Version(self.version) <= "2.1":
            self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst=os.path.join("include", "argparse"))
        else:
            self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "argparse"
        self.cpp_info.names["cmake_find_package_multi"] = "argparse"
        self.cpp_info.names["pkg_config"] = "argparse"
        if tools.Version(self.version) <= "2.1":
            self.cpp_info.includedirs.append(os.path.join("include", "argparse"))

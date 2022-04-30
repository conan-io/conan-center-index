from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class TabulateConan(ConanFile):
    name = "tabulate"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/tabulate"
    description = "Table Maker for Modern C++"
    topics = ("header-only", "cpp17", "tabulate", "table", "cli")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "17" if tools.Version(self.version) < "1.3.0" else "11"

    @property
    def _min_compiler_cpp17(self):
        return {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6",
            "apple-clang": "10.0",
        }

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        if tools.Version(self.version) < "1.3.0":
            compiler = str(self.settings.compiler)
            compiler_version = tools.Version(self.settings.compiler.version)

            if compiler in self._min_compiler_cpp17 and compiler_version < self._min_compiler_cpp17[compiler]:
                raise ConanInvalidConfiguration(
                    "{} {} requires a compiler that supports at least C++{}. "
                    "{} {} is not supported.".format(
                        self.name, self.version, self._min_cppstd,
                        compiler, compiler_version,
                    )
                )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tabulate")
        self.cpp_info.set_property("cmake_target_name", "tabulate::tabulate")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

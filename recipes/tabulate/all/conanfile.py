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

    def package_id(self):
        self.info.header_only()

    def validate(self):
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        else:
            self.output.warn("%s recipe lacks information about the %s compiler"
                             " standard version support" % (self.name, compiler))

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6",
            "apple-clang": "10.0"
        }

        if compiler not in minimal_version:
            self.output.info("%s requires a compiler that supports at least"
                             " C++17" % self.name)
            return

        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports"
                                            " at least C++17. %s %s is not"
                                            " supported." % (self.name, compiler, tools.Version(self.settings.compiler.version)))

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

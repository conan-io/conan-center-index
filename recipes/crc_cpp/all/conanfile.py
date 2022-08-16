from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class Crc_CppConan(ConanFile):
    name = "crc_cpp"
    description = "A header only constexpr / compile time small-table based CRC library for C++17 and newer"
    topics = "crc_cpp", "crc", "constexpr", "cpp17", "cpp20", "header-only"
    settings = "compiler", "os"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AshleyRoll/crc_cpp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _supported_compiler(self):
        compiler = str(self.settings.compiler)
        version = tools.scm.Version(self.settings.compiler.version)
        if compiler == "Visual Studio" and version >= "15":
            return True
        elif compiler == "gcc" and version >= "9":
            return True
        elif compiler == "clang" and version >= "5":
            return True
        elif compiler == "apple-clang" and version >= "10":
            return True
        else:
            self.output.warn("{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
        return False

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "17")
        if not self._supported_compiler:
            raise ConanInvalidConfiguration("crc_cpp: Unsupported compiler: {}-{} "
                                            "Minimum C++17 constexpr features required.".format(self.settings.compiler, self.settings.compiler.version))
    def source(self):
       tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

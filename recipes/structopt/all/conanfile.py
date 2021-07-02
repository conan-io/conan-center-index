import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class StructoptConan(ConanFile):
    name = "structopt"
    homepage = "https://github.com/p-ranav/structopt"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Parse command line arguments by defining a struct+"
    license = "MIT"
    settings = "compiler", "os"
    topics = ("conan", "structopt", "argument-parser", "cpp17", "header-only",
        "single-header-lib", "header-library", "command-line", "arguments",
        "mit-license", "modern-cpp", "structopt", "lightweight", "reflection",
        "cross-platform", "library", "type-safety", "type-safe", "argparse",
        "clap", "visit-struct-library", "magic-enum")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _supported_compiler(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
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

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self._supported_compiler:
            raise ConanInvalidConfiguration("structopt: Unsupported compiler: {}-{} "
                                            "(https://github.com/p-ranav/structopt#compiler-compatibility).".format(self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_id(self):
        self.info.header_only()

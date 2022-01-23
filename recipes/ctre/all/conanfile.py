import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class CtreConan(ConanFile):
    name = "ctre"
    homepage = "https://github.com/hanickadot/compile-time-regular-expressions"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Compile Time Regular Expression for C++17/20"
    topics = ("cpp17", "regex", "compile-time-regular-expressions")
    license = ("Apache-2.0", "LLVM-exception")
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)

        min_gcc = "7.4" if tools.Version(self.version) < "3" else "8"
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if (compiler == "Visual Studio" or compiler == "msvc") and version < "15":
            raise ConanInvalidConfiguration("ctre doesn't support MSVC < 15")
        elif compiler == "gcc" and version < min_gcc:
            raise ConanInvalidConfiguration("ctre doesn't support gcc < {}".format(min_gcc))
        elif compiler == "clang" and version < "6.0":
            raise ConanInvalidConfiguration("ctre doesn't support clang < 6.0")
        elif compiler == "apple-clang" and version < "10.0":
            raise ConanInvalidConfiguration("ctre doesn't support Apple clang < 10.0")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)


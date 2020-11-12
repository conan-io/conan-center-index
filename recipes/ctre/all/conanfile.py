import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class CtreConan(ConanFile):
    name = "ctre"
    homepage = "https://github.com/hanickadot/compile-time-regular-expressions"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Compile Time Regular Expression for C++17/20"
    topics = ("cpp17", "regex", "compile-time-regular-expressions")
    license = ("Apache-2.0", "LLVM-exception")
    no_copy_source = True
    settings = "compiler"

    _source_name = "compile-time-regular-expressions"
    _source_subfolder = "source_subfolder"

    def _validate_compiler_settings(self):
        # See: https://github.com/hanickadot/compile-time-regular-expressions#supported-compilers
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)

        min_gcc = "7.4" if self.version < "3" else "8"
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if compiler == "Visual Studio" and version < "15":
            raise ConanInvalidConfiguration("ctre doesn't support MSVC < 15")
        elif compiler == "gcc" and version < min_gcc:
            raise ConanInvalidConfiguration("ctre doesn't support gcc < {}".format(min_gcc))
        elif compiler == "clang" and version < "6.0":
            raise ConanInvalidConfiguration("ctre doesn't support clang < 6.0")
        elif compiler == "apple-clang" and version < "10.0":
            raise ConanInvalidConfiguration("ctre doesn't support Apple clang < 10.0")

    def configure(self):
         self._validate_compiler_settings()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self._source_name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()


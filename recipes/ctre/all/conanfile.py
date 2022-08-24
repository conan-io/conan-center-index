import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc

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
        compiler_version = tools.Version(self.settings.compiler.version)
        ctre_version = tools.Version(self.version)

        min_gcc = "7.4" if ctre_version < "3" else "8"
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if is_msvc(self):
            if compiler_version < "15":
                raise ConanInvalidConfiguration("{}/{} doesn't support MSVC < 15".format(self.name, self.version))
            if ctre_version >= "3.7" and compiler_version < 16:
                raise ConanInvalidConfiguration("{}/{} doesn't support MSVC < 16".format(self.name, self.version))
        elif compiler == "gcc" and compiler_version < min_gcc:
            raise ConanInvalidConfiguration("{}/{} doesn't support gcc < {}".format(self.name, self.version, min_gcc))
        elif compiler == "clang" and compiler_version < "6.0":
            raise ConanInvalidConfiguration("{}/{} doesn't support clang < 6.0".format(self.name, self.version))
        elif compiler == "apple-clang":
            if compiler_version < "10.0":
                raise ConanInvalidConfiguration("{}/{} doesn't support Apple clang < 10.0".format(self.name, self.version))
            # "library does not compile with (at least) Xcode 12.0-12.4"
            # https://github.com/hanickadot/compile-time-regular-expressions/issues/188
            # it's also occurred in Xcode 13.
            if ctre_version.major == "3" and ctre_version.minor == "4" and compiler_version >= "12":
                raise ConanInvalidConfiguration("{}/{} doesn't support Apple clang".format(self.name, self.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)


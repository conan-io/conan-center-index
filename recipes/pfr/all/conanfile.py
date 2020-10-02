from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibnameConan(ConanFile):
    name = "pfr"
    description = "std::tuple like methods for user defined types without any macro or boilerplate code"
    topics = ("conan", "boost", "pfr", "reflection", "magic_get")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apolukhin/magic_get"
    license = "BSL-1.0"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "9.4",
            "clang": "3.8",
            "gcc": "5.5"
        }

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

        compiler = self.settings.compiler
        try:
            min_version = self._minimum_compilers_version[str(compiler)]
            if tools.Version(compiler.version) < min_version:
                msg = (
                    "{} requires C++{} features which are not supported by compiler {} {}."
                ).format(self.name, self._minimum_cpp_standard, compiler, compiler.version)
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                "{} recipe lacks information about the {} compiler, "
                "support for the required C++{} features is assumed"
            ).format(self.name, compiler, self._minimum_cpp_standard)
            self.output.warn(msg)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        extracted_dir = "magic_get-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.download(**self.conan_data["sources"][self.version][1])

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="BSL-1.0.txt", dst="licenses", src=self.source_folder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()

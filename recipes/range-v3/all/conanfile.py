import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version, check_min_cppstd

class Rangev3Conan(ConanFile):
    name = "range-v3"
    license = "BSL-1.0"
    homepage = "https://github.com/ericniebler/range-v3"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Experimental range library for C++11/14/17"
    topics = ("range", "range-library", "proposal", "iterator", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def _validate_compiler_settings(self):
        # As per https://github.com/ericniebler/range-v3#supported-compilers
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)

        if compiler == "Visual Studio":
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, "20")

            if version < "16":
                raise ConanInvalidConfiguration("range-v3 doesn't support MSVC < 16")

        elif compiler == "gcc" and version < "6.5":
            raise ConanInvalidConfiguration("range-v3 doesn't support gcc < 6.5")

        elif compiler == "clang" and version < "3.9":
            raise ConanInvalidConfiguration("range-v3 doesn't support clang < 3.9")

    def configure(self):
        version = Version(self.version)
        if version >= "0.10":
            self._validate_compiler_settings()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version, check_min_cppstd
import os


class MPUnitsConan(ConanFile):
    name = "mp-units"
    homepage = "https://github.com/mpusz/units"
    description = "Physical Units library for C++"
    topics = ("units", "dimensions", "quantities", "dimensional-analysis", "physical-quantities", "physical-units", "system-of-units", "cpp23", "cpp20", "library", "quantity-manipulation")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    requires = (
        "fmt/7.0.3",
        "ms-gsl/3.1.0"
    )
    generators = "cmake"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        if compiler == "gcc":
            if version < "9.3":
                raise ConanInvalidConfiguration("mp-units requires at least g++-9.3")
        elif compiler == "Visual Studio":
            if version < "16":
                raise ConanInvalidConfiguration("mp-units requires at least MSVC 16")
        else:
            raise ConanInvalidConfiguration("mp-units is supported only by gcc and Visual Studio so far")
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, "20")

    def configure(self):
        self._validate_compiler_settings()

    def requirements(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        if (compiler == "gcc" and version < "10"):
            self.requires("range-v3/0.11.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "units-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "src", "include"))
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.settings.clear()
        self.info.settings.compiler = self.settings.compiler
        self.info.settings.compiler.version = self.settings.compiler.version

    def package_info(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        if compiler == "gcc":
            self.cpp_info.cxxflags = [
                "-Wno-literal-suffix",
                "-Wno-non-template-friend",
            ]
            if version < "10":
                self.cpp_info.cxxflags.extend([
                    "-fconcepts"
                ])
        elif compiler == "Visual Studio":
            self.cpp_info.cxxflags = [
                "/utf-8",
                "/wd4455"
            ]

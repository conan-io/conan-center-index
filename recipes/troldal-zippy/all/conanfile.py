from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class TroldalZippyConan(ConanFile):
    name = "troldal-zippy"
    description = "A simple C++ wrapper around the \"miniz\" zip library "
    topics = ("wrapper", "compression", "zip")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/troldal/Zippy"
    license = "MIT"
    settings = "compiler"
    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("miniz/2.2.0")

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "17",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "library"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        # To match the target created here
        # https://github.com/troldal/Zippy/blob/a838de8522f9051df0d1b202473bb6befe648702/library/CMakeLists.txt#L10
        self.cpp_info.filenames["cmake_find_package"] = "Zippy"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Zippy"
        self.cpp_info.names["cmake_find_package"] = "Zippy"
        self.cpp_info.names["cmake_find_package_multi"] = "Zippy"

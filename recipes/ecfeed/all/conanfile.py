from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class EcFeedConan(ConanFile):
    name = "ecfeed"
    license = "EPL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ecfeed.com/"
    description = "An open library used to connect to the ecFeed service. \
        It can be integrated with the most common testing frameworks \
        and generates a stream of test cases using a selected algorithm \
        (e.g. Cartesian, N-Wise)."
    topics = ("test", "ecfeed", "nwise")
    requires = "libcurl/7.80.0", "openssl/1.1.1n"
    settings = "os", "build_type", "arch", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
    @property
    def _compilers_minimum_version(self):
            minimum_versions = {
                "gcc": "8",
                "Visual Studio": "17",
                "msvc": "19.22",
                "clang": "6",
                "apple-clang": "10"
            }
            return minimum_versions
        
    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++20, " 
                    "which your compiler ({} {}) does not support.".format(
                        self.settings.compiler, self.settings.compiler.version))
        else:
            self.output.warn(
                f"{self.name} requires C++20. Your compiler is unknown. " 
                    "Assuming it supports C++20.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, 
                  destination=self._source_subfolder)

    def package(self):
        self.copy("ecfeed.hpp", 
                  dst="include", src=os.path.join(self._source_subfolder, "src"))
        self.copy("license.txt", 
                  dst="licenses", src=os.path.join(self._source_subfolder))

    def package_id(self):
        self.info.header_only()

from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class FakeItConan(ConanFile):
    name = "fakeit"
    description = "C++ mocking made easy. A simple yet very expressive, headers only library for c++ mocking."
    topics = ("mock", "fake", "spy")
    license = "MIT"
    homepage = "https://github.com/eranpeer/FakeIt"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "integration": ["boost", "catch", "cute", "gtest", "mettle", "nunit", "mstest", "qtest", "standalone", "tpunit"]
    }
    default_options = {"integration": "standalone"}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.integration == "boost":
            self.requires("boost/1.79.0")
        elif self.options.integration == "catch":
            self.requires("catch2/2.13.9")
        elif self.options.integration == "gtest":
            self.requires("gtest/1.11.0")
        elif self.options.integration == "qtest":
            self.requires("qt/6.3.0")
        elif self.options.integration == "standalone":
            pass
        else:
            raise ConanInvalidConfiguration("%s is not (yet) available on cci" % self.options.integration)

    def package_id(self):
        self.info.header_only()

    def validate(self):
        minimal_cpp_standard = "11"
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, minimal_cpp_standard)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="fakeit.hpp", dst="include", src=os.path.join(self._source_subfolder, "single_header", str(self.options.integration)))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class FakeItConan(ConanFile):
    name = "fakeit"
    license = "MIT"
    homepage = "https://github.com/eranpeer/FakeIt"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ mocking made easy. A simple yet very expressive, headers only library for c++ mocking."
    topics = ("mock", "fake", "spy")
    settings = "compiler"
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
            self.requires("boost/1.75.0")
        elif self.options.integration == "catch":
            self.requires("catch2/2.13.4")
        elif self.options.integration == "gtest":
            self.requires("gtest/cci.20210126")
        elif self.options.integration == "qtest":
            self.requires("qt/6.0.2")
        elif self.options.integration == "standalone":
            pass
        else:
            raise ConanInvalidConfiguration("%s is not (yet) available on cci" % self.options.integration)

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "FakeIt-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="fakeit.hpp", dst="include", src=os.path.join(self._source_subfolder, "single_header", str(self.options.integration)))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        del self.settings.compiler

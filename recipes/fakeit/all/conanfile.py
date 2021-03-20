from conans import ConanFile, tools
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
        "integration": [None, "boost", "catch", "cute", "gtest", "mettle", "nunit", "mstest", "qtest", "standalone",
                        "tpunit"]
    }
    default_options = {"integration": None}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "fakeit-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "single_header"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.integration is not None:
            config_dir = str(self.options.integration)
            self.cpp_info.includedirs.append(config_dir)

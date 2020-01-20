import os
from conans import ConanFile, tools


class ApprovalTestsCppConan(ConanFile):
    name = "approvaltests.cpp"
    version = "7.0.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/approvals/ApprovalTests.cpp"
    license = "Apache-2.0"
    description = "Approval Tests allow you to verify a chunk of output " \
                  "(such as a file) in one operation as opposed to writing " \
                  "test assertions for each element."
    topics = ("conan", "testing", "unit-testing", "header-only")
    options = {"test_framework": ["catch2", "gtest", "doctest", "boost"]}
    default_options = {"test_framework": "catch2"}
    exports_sources = "patches/*"
    no_copy_source = True

    @property
    def _header_file(self):
        return "ApprovalTests.hpp"

    def requirements(self):
        if self.options.test_framework == "catch2":
            self.requires("catch2/2.11.0")
        elif self.options.test_framework == "gtest":
            self.requires("gtest/1.10.0")
        elif self.options.test_framework == "doctest":
            self.requires("doctest/2.3.5")
        else:
            self.requires("boost/1.72.0")

    def source(self):
        for source in self.conan_data["sources"][self.version]:
            url = source["url"]
            filename = url[url.rfind("/") + 1:]
            tools.download(url, filename)
            tools.check_sha256(filename, source["sha256"])
        os.rename("ApprovalTests.v.{}.hpp".format(self.version),
                  self._header_file)

        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def package(self):
        self.copy(self._header_file, dst="include", src=self.source_folder)
        self.copy("LICENSE", dst="licenses", src=self.source_folder)

import os
from conans import ConanFile, tools
from conans.tools import Version


class ApprovalTestsCppConan(ConanFile):
    name = "approvaltests.cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/approvals/ApprovalTests.cpp"
    license = "Apache-2.0"
    description = "Approval Tests allow you to verify a chunk of output " \
                  "(such as a file) in one operation as opposed to writing " \
                  "test assertions for each element."
    topics = ("conan", "testing", "unit-testing", "header-only")
    options = {
        "with_boosttest": [True, False], # Should this be: with_boost_unit_test_framework?
        "with_catch2": [True, False],
        "with_gtest": [True, False],
        "with_doctest": [True, False]
    }
    default_options = {
        "with_boosttest": False,
        "with_catch2": False,
        "with_gtest": False,
        "with_doctest": False
    }
    no_copy_source = True

    def configure(self):
        if not self._boost_test_supported():
            del self.options.with_boosttest

    @property
    def _header_file(self):
        return "ApprovalTests.hpp"

    def requirements(self):
        if self.options.get_safe("with_boosttest"):
            self.requires("boost/1.72.0")
        if self.options.with_catch2:
            self.requires("catch2/2.11.0")
        if self.options.with_gtest:
            self.requires("gtest/1.10.0")
        if self.options.with_doctest:
            self.requires("doctest/2.3.6")

    def source(self):
        for source in self.conan_data["sources"][self.version]:
            url = source["url"]
            filename = url[url.rfind("/") + 1:]
            tools.download(url, filename)
            tools.check_sha256(filename, source["sha256"])
        os.rename("ApprovalTests.v.{}.hpp".format(self.version),
                  self._header_file)

    def package(self):
        self.copy(self._header_file, dst="include")
        self.copy("LICENSE", dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ApprovalTests"
        self.cpp_info.names["cmake_find_package_multi"] = "ApprovalTests"

    def package_id(self):
        self.info.header_only()

    def _boost_test_supported(self):
        return Version(self.version) >= "8.6.0"

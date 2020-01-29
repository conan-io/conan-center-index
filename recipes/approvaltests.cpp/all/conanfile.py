import os
from conans import ConanFile, tools


class ApprovalTestsCppConan(ConanFile):
    name = "approvaltests.cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/approvals/ApprovalTests.cpp"
    license = "Apache-2.0"
    description = "Approval Tests allow you to verify a chunk of output " \
                  "(such as a file) in one operation as opposed to writing " \
                  "test assertions for each element."
    topics = ("conan", "testing", "unit-testing", "header-only")
    no_copy_source = True

    @property
    def _header_file(self):
        return "ApprovalTests.hpp"

    def source(self):
        for source in self.conan_data["sources"][self.version]:
            url = source["url"]
            filename = url[url.rfind("/") + 1:]
            tools.download(url, filename)
            tools.check_sha256(filename, source["sha256"])
        os.rename("ApprovalTests.v.{}.hpp".format(self.version),
                  self._header_file)

    def package(self):
        self.copy(self._header_file, dst="include", src=self.source_folder)
        self.copy("LICENSE", dst="licenses", src=self.source_folder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ApprovalTests"
        self.cpp_info.names["cmake_find_package_multi"] = "ApprovalTests"

import os
from conans import ConanFile, CMake, tools


class ApprovalTestsCppConan(ConanFile):
    name = "approval-tests-cpp"
    version = "7.0.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/approvals/ApprovalTests.cpp"
    license = "Apache-2.0"
    description = "Approval Tests allow you to verify a chunk of output " \
                  "(such as a file) in one operation as opposed to writing " \
                  "test assertions for each element."
    topics = ("conan", "testing", "unit-testing", "header-only")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ['patches/*']
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        self.requires.add("Catch2/2.11.0@catchorg/stable")

    def source(self):
        tools.download(self.conan_data["sources"][self.version]["url"],
                       "ApprovalTests.hpp")
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def package(self):
        self.copy(pattern="ApprovalTests.hpp", dst="include/")

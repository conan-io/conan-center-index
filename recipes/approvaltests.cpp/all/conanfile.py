from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, download, rename
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53"


class ApprovalTestsCppConan(ConanFile):
    name = "approvaltests.cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/approvals/ApprovalTests.cpp"
    license = "Apache-2.0"
    description = "Approval Tests allow you to verify a chunk of output " \
                  "(such as a file) in one operation as opposed to writing " \
                  "test assertions for each element."
    topics = ("testing", "unit-testing", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_boosttest": [True, False],
        "with_catch2": [True, False],
        "with_gtest": [True, False],
        "with_doctest": [True, False],
        "with_cpputest": [True, False],
    }
    default_options = {
        "with_boosttest": False,
        "with_catch2": False,
        "with_gtest": False,
        "with_doctest": False,
        "with_cpputest": False,
    }
    no_copy_source = True

    @property
    def _header_file(self):
        return "ApprovalTests.hpp"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_boosttest:
            self.requires("boost/1.83.0")
        if self.options.with_catch2:
            self.requires("catch2/[>=3.5.0 <4]")
        if self.options.with_gtest:
            self.requires("gtest/[>=1.14.0 <2]")
        if self.options.with_doctest:
            self.requires("doctest/2.4.11")
        if self.options.get_safe("with_cpputest"):
            self.requires("cpputest/4.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        for source in self.conan_data["sources"][self.version]:
            urls = source["url"]
            url = urls[0] if isinstance(urls, (list, tuple)) else urls
            filename = url[url.rfind("/") + 1:]
            download(self, urls, filename, sha256=source["sha256"])
        rename(self, src=os.path.join(self.source_folder, f"ApprovalTests.v.{self.version}.hpp"),
                     dst=os.path.join(self.source_folder, self._header_file))

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, self._header_file, src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ApprovalTests")
        self.cpp_info.set_property("cmake_target_name", "ApprovalTests::ApprovalTests")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

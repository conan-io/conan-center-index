from conan import ConanFile
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import check_sha256, copy, download, rename
import os

required_conan_version = ">=1.43.0"


class ApprovalTestsCppConan(ConanFile):
    name = "approvaltests.cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/approvals/ApprovalTests.cpp"
    license = "Apache-2.0"
    description = "Approval Tests allow you to verify a chunk of output " \
                  "(such as a file) in one operation as opposed to writing " \
                  "test assertions for each element."
    topics = ("testing", "unit-testing", "header-only")
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
    settings = "compiler", "os", "build_type", "arch"

    @property
    def _header_file(self):
        return "ApprovalTests.hpp"

    def configure(self):
        if not self._boost_test_supported():
            del self.options.with_boosttest
        if not self._cpputest_supported():
            del self.options.with_cpputest

    def validate(self):
        self._validate_compiler_settings()

    def requirements(self):
        if self.options.get_safe("with_boosttest"):
            self.requires("boost/1.72.0")
        if self.options.with_catch2:
            self.requires("catch2/2.13.7")
        if self.options.with_gtest:
            self.requires("gtest/1.10.0")
        if self.options.with_doctest:
            self.requires("doctest/2.4.6")
        if self.options.get_safe("with_cpputest"):
            self.requires("cpputest/4.0")

    def package_id(self):
        self.info.clear()

    def source(self):
        for source in self.conan_data["sources"][self.version]:
            url = source["url"]
            filename = url[url.rfind("/") + 1:]
            download(self, url, filename)
            check_sha256(self, filename, source["sha256"])
        rename(self, f"ApprovalTests.v.{self.version}.hpp", self._header_file)

    def package(self):
        copy(self, self._header_file, src=self.source_folder, dst=os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ApprovalTests")
        self.cpp_info.set_property("cmake_target_name", "ApprovalTests::ApprovalTests")

        self.cpp_info.names["cmake_find_package"] = "ApprovalTests"
        self.cpp_info.names["cmake_find_package_multi"] = "ApprovalTests"

    def _boost_test_supported(self):
        return Version(self.version) >= "8.6.0"

    def _cpputest_supported(self):
        return Version(self.version) >= "10.4.0"

    def _std_puttime_required(self):
        return Version(self.version) >= "10.2.0"

    def _validate_compiler_settings(self):
        if self._std_puttime_required():
            self._require_at_least_compiler_version("gcc", 5)

    def _require_at_least_compiler_version(self, compiler, compiler_version):
        if self.info.settings.compiler == compiler and Version(self.info.settings.compiler.version) < compiler_version:
            raise ConanInvalidConfiguration(
                f"{self.name}/{self.version} with compiler {compiler} requires at least compiler version {compiler_version}")

from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class TranswarpConan(ConanFile):
    name = "transwarp"
    description = "A header-only C++ library for task concurrency."
    license = "MIT"
    topics = ("transwarp", "concurrency", "asynchronous")
    homepage = "https://github.com/bloomen/transwarp"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

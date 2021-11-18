from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class WilzegersAutotestConan(ConanFile):
    name = "wilzegers_autotest"
    version = "0.1"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/wilzegers/autotest"
    description = "Autotest facilitates the testing of class interfaces"
    topics = ("autotest", "testing")
    settings = "compiler"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.settings.compiler != 'clang':
            raise ConanInvalidConfiguration("Only clang allowed")

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "autotest/include"), dst="include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "wilzegers_autotest"
        self.cpp_info.names["cmake_find_package_multi"] = "wilzegers_autotest"
        self.cpp_info.names["pkg_config"] = "wilzegers_autotest"

from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration
import os

requires_conan_version = ">=1.33.0"


class WilzegersAutotestConan(ConanFile):
    name = "wilzegers-autotest"
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
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration("Only clang allowed")

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "autotest/include"), dst="include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

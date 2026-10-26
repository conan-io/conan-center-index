from conan import ConanFile
from conan.tools.files import copy, get
import os

required_conan_version = ">=2.4"


class DoxygenAwesomeCssConan(ConanFile):
    name = "doxygen-awesome-css"
    description = "Custom CSS theme for doxygen html-documentation with lots of customization parameters."
    topics = ("documentation", "theme")
    homepage = "https://jothepro.github.io/doxygen-awesome-css/"
    license = "MIT"
    url = "https://github.com/jothepro/doxygen-awesome-css"
    package_type = "unknown"
    settings = ()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "doxygen-awesome-**", src=self.source_folder, dst=self.package_folder)

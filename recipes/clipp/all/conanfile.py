import os
from conan import ConanFile, tools


required_conan_version = ">=1.46.0"

class ClippConan(ConanFile):
    name = "clipp"
    description = """Easy to use, powerful & expressive command line argument parsing for modern C++ / single header / usage & doc generation."""
    topics = ("clipp", "argparse", "cli", "usage", "options", "subcommands")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/muellan/clipp"
    license = "MIT"
    no_copy_source = True

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def package(self):
        tools.files.copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        tools.files.copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

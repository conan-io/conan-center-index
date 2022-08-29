from conan import ConanFile
from conan.tools import files

required_conan_version = ">=1.45.0"


class libhal_conan(ConanFile):
    name = "libhal"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libhal.github.io/libhal"
    description = ("A collection of interfaces and abstractions for embedded "
                   "peripherals and devices using modern C++")
    topics = ("peripherals", "hardware", "abstraction", "devices")
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True

    def package(self):
        self.copy("*LICENSE*", dst="licenses", keep_path=False)
        self.copy("*.h", src="include/", dst="include/")
        self.copy("*.hpp", src="include/", dst="include/")

    def package_id(self):
        self.info.header_only()

    def source(self):
        files.get(self,
                  **self.conan_data["sources"][self.version], strip_root=True)

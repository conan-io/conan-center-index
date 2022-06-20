import os

from conan import ConanFile
from conan.tools.files import get

required_conan_version = ">=1.45.0"

class OutPtrConan(ConanFile):
    name = "out_ptr"

    # Optional metadata
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/soasis/out_ptr"
    description = "a C++11 implementation of std::out_ptr (p1132), as a standalone library"
    topics = ("utility", "backport")
    settings = "os", "arch", "build_type", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

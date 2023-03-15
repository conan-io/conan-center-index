import os 
from conan import ConanFile
from conan.tools.files import get, copy
from glob import glob

required_conan_version = ">=1.52.0"

class PackageConan(ConanFile):
    name = "detect"
    description = "A single header library to detect the OS at compile time."
    license = "MIT"

    author = "Joel Lefkowitz joellefkowitz@hotmail.com"
    url = "https://github.com/JoelLefkowitz/detect"
    homepage = "https://github.com/project/package"

    topics = ("os", "header-only")
    settings = ("os", "arch", "compiler", "build_type")
    
    no_copy_source = True
    exports_sources = "src/*"

    @property
    def _min_cppstd(self):
        return 11

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_id(self):-
        self.info.clear()

    def package_info(self):
        self.cpp_info.libs = ["detect"]

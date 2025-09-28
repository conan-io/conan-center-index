import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

class CppMemberAccessorConan(ConanFile):
    name = "cpp-member-accessor"
    version = "1.0.0"
    license = "MIT"
    author = "Hubert Liberacki <hliberacki@gmail.com>"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hliberacki/cpp-member-accessor"
    topics = ("c++", "templates", "access-private-members", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "include/*"
    no_copy_source = True
    package_type = "header-library"
    exports = "LICENSE"

    @property
    def _min_cppstd(self):
        return 14

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def layout(self):
        basic_layout(self)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.hpp", self.source_folder, self.package_folder)
    
    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

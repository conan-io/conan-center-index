from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2"

class BarkeepConan(ConanFile):
    name = "barkeep"
    description = "Small C++ header to display async animations, counters, progress bars, and status messages"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oir/barkeep"
    topics = ("cli", "counter", "progress-bar", "animation", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include", "barkeep"),
            src=os.path.join(self.source_folder, "barkeep"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if (is_msvc(self)):
            self.cpp_info.cxxflags.append("/permissive-")

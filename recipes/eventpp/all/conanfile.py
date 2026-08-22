from conan import ConanFile
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.51.1"

class EventppConan(ConanFile):
    name = "eventpp"
    description = "Event Dispatcher and callback list for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wqking/eventpp"
    topics = ("observer-pattern", "event-dispatcher", "signal", "slot", "publish-subscribe", "nested-events", "thread-safe", "header-only")
    
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")
           
    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="license", 
             dst=os.path.join(self.package_folder, "licenses"), 
             src=self.source_folder)
        copy(self, pattern="*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

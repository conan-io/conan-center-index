import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.1"


class NinjaHSMConan(ConanFile):
    name = "ninjahsm"
    description = (
        "A small, simple hierarchical state machine (HSM) library for C++ embedded systems. "
        "Header-only, no dynamic memory allocation."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gbmhunter/NinjaHSM"
    topics = ("state-machine", "hsm", "statechart", "embedded", "fsm", "hierarchical", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # NinjaHSM's public headers include <etl/delegate.h>, so ETL must be visible to consumers.
        self.requires("etl/20.39.4", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*.hpp",
            src=os.path.join(self.source_folder, "src"),
            dst=os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

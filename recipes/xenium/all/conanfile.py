from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.0"

class XeniumConan(ConanFile):
    name = "xenium"
    description = "A C++ library providing various concurrent data structures and reclamation schemes"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mpoeter/xenium"
    topics = ("parallelism", "lockfree", "reclamation", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.arch not in ("x86_64", "armv8", "armv8.3", "arm64ec", "sparc", "sparcv9"):
            raise ConanInvalidConfiguration(f"{self.ref} only supports x86_64, armv8, armv8.3, arm64ec, sparc, and sparcv9 architecture.")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include", "xenium"),
            src=os.path.join(self.source_folder, "xenium"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class MikeLankampFpmConan(ConanFile):
    name = "mikelankamp-fpm"
    description = "C++ header-only fixed-point math library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/MikeLankamp/fpm"
    topics = ("fixed-point", "math", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "fpm")
        self.cpp_info.set_property("cmake_target_name", "fpm::fpm")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "fpm"
        self.cpp_info.filenames["cmake_find_package_multi"] = "fpm"
        self.cpp_info.names["cmake_find_package"] = "fpm"
        self.cpp_info.names["cmake_find_package_multi"] = "fpm"

from pathlib import Path

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake

required_conan_version = ">=2.1"


class IsptrRecipe(ConanFile):

    name = "intrusive_shared_ptr"
    description = "Intrusive reference counting smart pointer, highly configurable reference counted base class and various adapters."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gershnik/intrusive_shared_ptr"
    topics = ("smart-pointer", "intrusive", "header-only", "header-library")

    generators = "CMakeToolchain"
    settings = "os", "arch", "build_type", "compiler"
    package_type = "header-library"
    no_copy_source = True

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25]")

    def validate(self):
        check_min_cppstd(self, 17)

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", src=self.source_folder, dst=Path(self.package_folder) / "licenses")
        cmake = CMake(self)
        cmake.install()
        rmdir(self, Path(self.package_folder) / "share")
        rm(self, "*.cmake", Path(self.package_folder) / "lib" / "isptr")

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "isptr")
        self.cpp_info.set_property("cmake_target_name", "isptr::isptr")
        self.cpp_info.set_property("pkg_config_name",  "isptr")

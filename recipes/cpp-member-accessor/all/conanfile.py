import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir


class CppMemberAccessorConan(ConanFile):
    name = "cpp-member-accessor"
    description = "Library providing legal access to C++ private members"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hliberacki/cpp-member-accessor"
    topics = ("c++", "templates", "access-private-members", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    package_type = "header-library"

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
    
    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "accessor")
        self.cpp_info.set_property("cmake_target_aliases", ["accessor"])
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

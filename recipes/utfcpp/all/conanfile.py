from conan import ConanFile
from conan.tools.files import copy, get, rmdir
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
import os


required_conan_version = ">=2.1"


class UtfCppConan(ConanFile):
    name = "utfcpp"
    description = "UTF-8 with C++ in a Portable Way"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nemtrif/utfcpp"
    topics = ("utf", "utf8", "unicode", "text", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "utf8cpp")
        self.cpp_info.set_property("cmake_target_name", "utf8cpp::utf8cpp")
        # FIXME: Keep CMake target utf8cpp for backward compatibility as more projects are using it in CCI.
        self.cpp_info.set_property("cmake_target_aliases", ["utf8::cpp", "utf8cpp"])
        self.cpp_info.includedirs.append(os.path.join("include", "utf8cpp"))

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

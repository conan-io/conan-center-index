from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import chdir, copy, get, rename, rmdir
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class BlazeConan(ConanFile):
    name = "blaze"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/blaze-lib/blaze"
    description = "open-source, high-performance C++ math library for dense and sparse arithmetic"
    topics = ("blaze", "math", "algebra", "linear algebra", "high-performance")
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        base_source_dir = os.path.join(self.source_folder, os.pardir)
        get(self, **self.conan_data["sources"][self.version],
            destination=base_source_dir, strip_root=True)
        with chdir(self, base_source_dir):
            rmdir(self, self.source_folder)
            rename(self, src=f"blaze-{self.version}", dst=self.source_folder)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "blaze/*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "blaze")
        self.cpp_info.set_property("cmake_target_name", "blaze::blaze")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

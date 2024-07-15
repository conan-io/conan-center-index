from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches, replace_in_file
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class PlflistConan(ConanFile):
    name = "plf_list"
    description = "plf::list is a drop-in higher-performance replacement for std::list"
    license = "Zlib"
    topics = ("container", "linked-list", "list", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mattreecebentley/plf_list"
    settings = "os", "arch", "compiler", "build_type"
    def export_sources(self):
        export_conandata_patches(self)

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 98)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        # Do not set PLF_TYPE_TRAITS_SUPPORT fo GCC v5.
        # Tries and fails to use std::allocator_traits<allocator_type>::is_always_equal otherwise.
        replace_in_file(self, os.path.join(self.source_folder, "plf_list.h"),
                        "#if __GNUC__ >= 5 // GCC v4.9 and below do not support std::is_trivially_copyable",
                        "#if __GNUC__ >= 6 // GCC v4.9 and below do not support std::is_trivially_copyable")

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "plf_list.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

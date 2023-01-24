from conan import ConanFile
from conan.tools.files import copy, get, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
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
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        # apple-clang 14 defaults C++ 20, but it doesn't support C++20 features little
        # https://www.reddit.com/r/cpp/comments/v6ydea/xcode_now_defaults_to_c20/
        if Version(self.version) >= "2.50":
            replace_in_file(self, os.path.join(self.source_folder, "plf_list.h"),
            "if __cplusplus > 201704L && ((defined(_LIBCPP_VERSION) && _LIBCPP_VERSION >= 13) || !defined(_LIBCPP_VERSION)) && ((defined(__clang__) && (__clang_major__ >= 13)) || (defined(__GNUC__) && __GNUC__ >= 10) || (!defined(__clang__) && !defined(__GNUC__)))",
            "if __cplusplus > 201704L && ((defined(_LIBCPP_VERSION) && _LIBCPP_VERSION >= 13) || !defined(_LIBCPP_VERSION)) && (!defined(__APPLE_CC__) && (defined(__clang__) && (__clang_major__ >= 13)) || (defined(__GNUC__) && __GNUC__ >= 10) || (!defined(__clang__) && !defined(__GNUC__)))"
            )

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "plf_list.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

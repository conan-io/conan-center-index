from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class CpphttplibConan(ConanFile):
    name = "cpp-httplib"
    description = "A C++11 single-file header-only cross platform HTTP/HTTPS library."
    license = "MIT"
    topics = ("cpp-httplib", "http", "https", "header-only")
    homepage = "https://github.com/yhirose/cpp-httplib"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_openssl": [True, False],
        "with_zlib": [True, False],
        "with_brotli": [True, False],
    }
    default_options = {
        "with_openssl": False,
        "with_zlib": False,
        "with_brotli": False,
    }

    no_copy_source = True

    def config_options(self):
        if Version(self.version) < "0.7.2":
            del self.options.with_brotli

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.get_safe("with_brotli"):
            self.requires("brotli/1.0.9")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "httplib.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "httplib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "httplib")
        self.cpp_info.set_property("cmake_target_name", "httplib::httplib")
        self.cpp_info.includedirs.append(os.path.join("include", "httplib"))
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if self.options.with_openssl:
            self.cpp_info.defines.append("CPPHTTPLIB_OPENSSL_SUPPORT")
        if self.options.with_zlib:
            self.cpp_info.defines.append("CPPHTTPLIB_ZLIB_SUPPORT")
        if self.options.get_safe("with_brotli"):
            self.cpp_info.defines.append("CPPHTTPLIB_BROTLI_SUPPORT")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32", "cryptui", "ws2_32"]

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "httplib"
        self.cpp_info.names["cmake_find_package_multi"] = "httplib"

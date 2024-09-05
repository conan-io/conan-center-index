from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class CpphttplibConan(ConanFile):
    name = "http-request"
    description = "A modern C++ lightweight cross-platform HTTP request library."
    license = "MIT"
    homepage = "https://github.com/Nevermore1994/http-request"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("http", "https", "modern C++")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_openssl": [True, False]
    }
    default_options = {
        "with_openssl": True,
    }
    no_copy_source = True

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def package_id(self):
        self.info.clear()

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7.1",
            "msvc": "192",
            "Visual Studio": "15.3",
    }

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "public"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "http_request")
        self.cpp_info.set_property("cmake_target_name", "http_request::http_request")
        self.cpp_info.includedirs.append(os.path.join("include", "public"))
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.with_openssl:
            self.cpp_info.defines.append("ENABLE_HTTPS")
        if self.settings.os in ["Linux", "FreeBSD", "Macos", "Android", "iOS"]:
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32", "cryptui", "ws2_32"]

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "http_request"
        self.cpp_info.names["cmake_find_package_multi"] = "http_request"

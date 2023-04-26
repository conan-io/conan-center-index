from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, copy, rmdir
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


class RestinioConan(ConanFile):
    name = "restinio"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/restinio"
    url = "https://github.com/conan-io/conan-center-index"
    description = "RESTinio is a header-only C++14 library that gives you an embedded HTTP/Websocket server."
    topics = ("http-server", "websockets", "rest", "tls-support")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "asio": ["boost", "standalone"],
        "with_openssl": [True, False],
        "with_zlib": [True, False],
        "with_pcre": [1, 2, None],
    }
    default_options = {
        "asio": "standalone",
        "with_openssl": False,
        "with_zlib": False,
        "with_pcre": None,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("http_parser/2.9.4")

        if Version(self.version) >= "0.6.17":
            self.requires("fmt/9.1.0")
        elif Version(self.version) >= "0.6.16":
            self.requires("fmt/9.0.0")
        else:
            self.requires("fmt/8.1.1")

        self.requires("expected-lite/0.6.2")
        self.requires("optional-lite/3.5.0")
        self.requires("string-view-lite/1.6.0")
        self.requires("variant-lite/2.0.0")

        if self.options.asio == "standalone":
            if Version(self.version) >= "0.6.9":
                self.requires("asio/1.22.1")
            else:
                self.requires("asio/1.16.1")
        else:
            if Version(self.version) >= "0.6.9":
                self.requires("boost/1.781.0")
            else:
                self.requires("boost/1.73.0")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1t")

        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

        if self.options.with_pcre == 1:
            self.requires("pcre/8.45")
        elif self.options.with_pcre == 2:
            self.requires("pcre2/10.40")

    def package_id(self):
        self.info.clear()

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
        }
        check_min_vs(self, 190)
        if not is_msvc(self):
            minimum_version = minimal_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{minimal_cpp_standard}, which your compiler does not support."
                )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RESTINIO_INSTALL"] = True
        tc.variables["RESTINIO_FIND_DEPS"] = False
        tc.variables["RESTINIO_USE_EXTERNAL_EXPECTED_LITE"] = True
        tc.variables["RESTINIO_USE_EXTERNAL_OPTIONAL_LITE"] = True
        tc.variables["RESTINIO_USE_EXTERNAL_STRING_VIEW_LITE"] = True
        tc.variables["RESTINIO_USE_EXTERNAL_VARIANT_LITE"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "dev", "restinio"))
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "restinio")
        self.cpp_info.set_property("cmake_target_name", "restinio::restinio")
        self.cpp_info.defines.extend(["RESTINIO_EXTERNAL_EXPECTED_LITE", "RESTINIO_EXTERNAL_OPTIONAL_LITE",
                                      "RESTINIO_EXTERNAL_STRING_VIEW_LITE", "RESTINIO_EXTERNAL_VARIANT_LITE"])
        if self.options.asio == "boost":
            self.cpp_info.defines.append("RESTINIO_USE_BOOST_ASIO")

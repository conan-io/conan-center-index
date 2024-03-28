from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, apply_conandata_patches
import os

required_conan_version = ">=1.53.0"


class LibevhtpConan(ConanFile):
    name = "libevhtp"
    description = "Create extremely-fast and secure embedded HTTP servers with ease."
    topics = ("http", "networking", "async")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Yellow-Camper/libevhtp"
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_ssl": [True, False],
        "disable_evthr": [True, False],
        "disable_regex": [True, False],
        "use_jemalloc": [True, False],
        "use_tcmalloc": [True, False],
        "parse_query_body": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_ssl": False,
        "disable_evthr": False,
        "disable_regex": False,
        "use_jemalloc": False,
        "use_tcmalloc": False,
        "parse_query_body": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        if not self.options.disable_ssl:
            self.requires("openssl/[>=1.1 <4]")
        if not self.options.disable_regex:
            self.requires("oniguruma/[>=5.9.2]", headers=True)
        self.requires("libevent/[>=2]", options={
            "with_openssl": not self.options.disable_ssl
        })
        if self.options.use_jemalloc:
            self.requires("jemalloc/[*]", headers=True, libs=True, options={
                "shared": True
            })
        if self.options.use_tcmalloc:
            self.requires("gperftools/[*]", headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["EVHTP_DISABLE_SSL"] = self.options.disable_ssl
        tc.cache_variables["EVHTP_DISABLE_EVTHR"] = self.options.disable_evthr
        tc.cache_variables["EVHTP_DISABLE_REGEX"] = self.options.disable_regex
        tc.cache_variables["EVHTP_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["EVHTP_USE_JEMALLOC"] = self.options.use_jemalloc
        tc.cache_variables["EVHTP_USE_TCMALLOC"] = self.options.use_tcmalloc
        tc.cache_variables["EVHTP_PARSE_QUERY_BODY"] = self.options.parse_query_body
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libevhtp")
        self.cpp_info.set_property("pkg_config_name", "libevhtp")
        self.cpp_info.libs = ["evhtp"]


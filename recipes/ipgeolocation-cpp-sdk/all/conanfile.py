from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os


required_conan_version = ">=2.0.9"


class IpGeolocationCppSdkConan(ConanFile):
    name = "ipgeolocation-cpp-sdk"
    description = "Official C++ SDK for IPGeolocation.io IP location, ASN, timezone, hostname, abuse, user-agent, and security lookups."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/IPGeolocation/ip-geolocation-api-cpp-sdk"
    topics = (
        "ip-location",
        "ip-geolocation",
        "timezone",
        "asn",
        "hostname",
        "abuse",
        "user-agent",
        "security",
    )

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("libcurl/[>=8 <9]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires a compiler with C++17 support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["IPGEOLOCATION_BUILD_TESTS"] = False
        tc.cache_variables["IPGEOLOCATION_ENABLE_COVERAGE"] = False
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ipgeolocation")
        self.cpp_info.set_property("cmake_target_name", "ipgeolocation::ipgeolocation")
        self.cpp_info.libs = ["ipgeolocation"]
        self.cpp_info.requires = ["libcurl::curl"]

        if not is_msvc(self) and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54"


class OatppLibresslConan(ConanFile):
    name = "oatpp-libressl"
    license = "Apache-2.0"
    homepage = "https://github.com/oatpp/oatpp-libressl"
    url = "https://github.com/conan-io/conan-center-index"
    description = "oat++ libressl library"
    topics = ("oat++", "oatpp", "libressl")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # There's a 1 to 1 match between versions of oatpp and oatpp-libressl
        # oatpp-libressl/oatpp-libressl/Config.hpp:28 and 30 contain includes to these libraries
        self.requires(f"oatpp/{self.version}", transitive_headers=True)
        self.requires("libressl/3.5.3", transitive_headers=True)

    @property
    def _min_cppstd(self):
        return 11

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared library with msvc")

        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC >=5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OATPP_BUILD_TESTS"] = False
        tc.variables["OATPP_MODULES_LOCATION"] = "INSTALLED"
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "oatpp-libressl")
        self.cpp_info.set_property("cmake_target_name", "oatpp::oatpp-libressl")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: back to global scope in conan v2 once legacy generators removed
        self.cpp_info.components["_oatpp-libressl"].includedirs = [
            os.path.join("include", f"oatpp-{self.version}", "oatpp-libressl")
        ]
        self.cpp_info.components["_oatpp-libressl"].libdirs = [os.path.join("lib", f"oatpp-{self.version}")]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["_oatpp-libressl"].bindirs = [os.path.join("bin", f"oatpp-{self.version}")]
        else:
            self.cpp_info.components["_oatpp-libressl"].bindirs = []
        self.cpp_info.components["_oatpp-libressl"].libs = ["oatpp-libressl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_oatpp-libressl"].system_libs = ["pthread"]

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.filenames["cmake_find_package"] = "oatpp-libressl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "oatpp-libressl"
        self.cpp_info.names["cmake_find_package"] = "oatpp"
        self.cpp_info.names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.components["_oatpp-libressl"].names["cmake_find_package"] = "oatpp-libressl"
        self.cpp_info.components["_oatpp-libressl"].names["cmake_find_package_multi"] = "oatpp-libressl"
        self.cpp_info.components["_oatpp-libressl"].set_property("cmake_target_name", "oatpp::oatpp-libressl")
        self.cpp_info.components["_oatpp-libressl"].requires = ["oatpp::oatpp", "libressl::libressl"]

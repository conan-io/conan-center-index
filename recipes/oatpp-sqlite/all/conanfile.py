from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class OatppsqliteConan(ConanFile):
    name = "oatpp-sqlite"
    description = "SQLite adapter for oatpp ORM."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oatpp/oatpp-sqlite"
    topics = ("oat++", "oatpp", "sqlite")
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
        self.requires(f"oatpp/{self.version}", transitive_headers=True)
        self.requires("sqlite3/3.45.0")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared library with msvc")

        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC >=5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        self.cpp_info.set_property("cmake_file_name", "oatpp-sqlite")
        self.cpp_info.set_property("cmake_target_name", "oatpp::oatpp-sqlite")
        # TODO: back to global scope in conan v2 once legacy generators removed
        self.cpp_info.components["_oatpp-sqlite"].includedirs = [
            os.path.join("include", f"oatpp-{self.version}", "oatpp-sqlite")
        ]
        self.cpp_info.components["_oatpp-sqlite"].libdirs = [os.path.join("lib", f"oatpp-{self.version}")]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["_oatpp-sqlite"].bindirs = [os.path.join("bin", f"oatpp-{self.version}")]
        else:
            self.cpp_info.components["_oatpp-sqlite"].bindirs = []
        self.cpp_info.components["_oatpp-sqlite"].libs = ["oatpp-sqlite"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_oatpp-sqlite"].system_libs = ["pthread"]

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.filenames["cmake_find_package"] = "oatpp-sqlite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "oatpp-sqlite"
        self.cpp_info.names["cmake_find_package"] = "oatpp"
        self.cpp_info.names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.components["_oatpp-sqlite"].names["cmake_find_package"] = "oatpp-sqlite"
        self.cpp_info.components["_oatpp-sqlite"].names["cmake_find_package_multi"] = "oatpp-sqlite"
        self.cpp_info.components["_oatpp-sqlite"].set_property("cmake_target_name", "oatpp::oatpp-sqlite")
        self.cpp_info.components["_oatpp-sqlite"].requires = ["oatpp::oatpp", "sqlite3::sqlite3"]

from conan import ConanFile
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfigDeps
import os


required_conan_version = ">=2.1"


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    description = "SQLiteCpp is a smart and easy to use C++ sqlite3 wrapper"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SRombauts/SQLiteCpp"
    topics = ("sqlite", "sqlite3", "data-base")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "stack_protection": [True, False],
        "with_sqlcipher": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "stack_protection": True,
        "with_sqlcipher": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "3.3.1":
            del self.options.with_sqlcipher

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.get_safe("with_sqlcipher"):
            self.options["sqlcipher"].enable_column_metadata = True

    def requirements(self):
        if self.options.get_safe("with_sqlcipher"):
            self.requires("sqlcipher/4.6.1")
        else:
            self.requires("sqlite3/[>=3.45 <4]")

    def validate(self):
        check_min_cppstd(self, 11)
        
        if self.info.settings.os == "Windows" and self.info.options.shared:
            raise ConanInvalidConfiguration("SQLiteCpp can not be built as shared lib on Windows")
        if self.options.get_safe("with_sqlcipher")and Version(self.version) < "3.3.1":
            raise ConanInvalidConfiguration("Using SQLCipher with this recipe is only available from version 3.3.1")
        if self.options.get_safe("with_sqlcipher") and not self.dependencies["sqlcipher"].options.enable_column_metadata:
            raise ConanInvalidConfiguration(f"{self.ref} option with_sqlcipher=True requires 'sqlcipher/*:enable_column_metadata=True'")
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SQLITECPP_INTERNAL_SQLITE"] = False
        tc.variables["SQLITECPP_RUN_CPPLINT"] = False
        tc.variables["SQLITECPP_RUN_CPPCHECK"] = False
        tc.variables["SQLITECPP_RUN_DOXYGEN"] = False
        tc.variables["SQLITECPP_BUILD_EXAMPLES"] = False
        tc.variables["SQLITECPP_BUILD_TESTS"] = False
        tc.variables["SQLITECPP_USE_STACK_PROTECTION"] = self.options.stack_protection
        tc.variables["SQLITE_HAS_CODEC"] = self.options.get_safe("with_sqlcipher", False)
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

        if self.options.get_safe("with_sqlcipher"):
            pc = PkgConfigDeps(self)
            pc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SQLiteCpp")
        self.cpp_info.set_property("cmake_target_name", "SQLiteCpp")
        self.cpp_info.libs = ["SQLiteCpp"]
        if self.options.get_safe("with_sqlcipher"):
            self.cpp_info.defines.append("SQLITE_HAS_CODEC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]

        if self._is_mingw:
            self.cpp_info.system_libs = ["ssp"]


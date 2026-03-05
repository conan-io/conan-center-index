from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.1"

class LibpqxxConan(ConanFile):
    name = "libpqxx"
    description = "The official C++ client API for PostgreSQL"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jtv/libpqxx"
    topics = ("libpqxx", "postgres", "postgresql", "database", "db")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_shared_fpic"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libpq/[>=15.4 <18]")

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_DOC"] = False
        tc.cache_variables["BUILD_TEST"] = False
        tc.cache_variables["SKIP_BUILD_EXAMPLES"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libpqxx")
        self.cpp_info.set_property("cmake_target_name", "libpqxx::pqxx")
        self.cpp_info.set_property("pkg_config_name", "libpqxx")
        self.cpp_info.components["pqxx"].libs = ["pqxx"]
        if self.settings.os == "Windows":
            self.cpp_info.components["pqxx"].system_libs = ["wsock32", "ws2_32"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pqxx"].system_libs.append("m")

        self.cpp_info.components["pqxx"].set_property("cmake_target_name", "libpqxx::pqxx")
        self.cpp_info.components["pqxx"].set_property("pkg_config_name", "libpqxx")
        self.cpp_info.components["pqxx"].requires = ["libpq::pq"]
        if self.options.shared:
            self.cpp_info.components["pqxx"].defines = ["PQXX_SHARED"]

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.0.9"

class MariadbConnectorCppRecipe (ConanFile):
    name = "mariadb-connector-cpp"
    description = "MariaDB Connector/C++ is used to connect applications " \
                  "developed in C++ to MariaDB and MySQL databases."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mariadb.com/docs/server/connect/programming-languages/cpp"
    topics = ("mariadb", "mysql", "database")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dyncol": [True, False],
        "with_curl": [True, False],
        "with_ssl": [False, "openssl", "gnutls", "schannel"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "dyncol": True,
        "with_curl": True,
        "with_ssl": "openssl",
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_cmake_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.with_ssl = "schannel"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_curl:
            self.requires("libcurl/[>=7.78.0 <9]")

        # with_iconv doesn't exists on Windows (Why?)
        self.requires ("mariadb-connector-c/3.3.8", options={
            "dyncol": self.options.dyncol,
            "with_curl": self.options.with_curl,
            "with_ssl": self.options.with_ssl
        })

    def validate(self):
        check_min_cppstd(self, 14)
        if self.settings.os != "Windows" and self.options.with_ssl == "schannel":
            raise ConanInvalidConfiguration("schannel only supported on Windows")
        if self.options.with_ssl == "gnutls":
            raise ConanInvalidConfiguration("gnutls not yet available in CCI")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_mariadb_connector_cpp_INCLUDE"] = os.path.join(self.source_folder, "conan_cmake_project_include.cmake")
        tc.cache_variables["WITH_UNIT_TESTS"] = False
        tc.cache_variables["INSTALL_BINDIR"] = "bin"
        tc.cache_variables["INSTALL_LIBDIR"] = "lib"
        tc.cache_variables["INSTALL_PLUGINDIR"] = os.path.join("lib", "plugin").replace("\\", "/")
        tc.cache_variables["USE_SYSTEM_INSTALLED_LIB"] = True
        tc.cache_variables["MARIADB_LINK_DYNAMIC"] = True

        if self.settings.os == "Windows":
            tc.cache_variables["CONC_WITH_MSI"] = False
            tc.cache_variables["WITH_MSI"] = False

        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install(component="Headers")
        if self.options.shared:
            cmake.install(component="SharedLibraries")
        else:
            cmake.install(component="Development")

        copy(self, "COPYING", src=os.path.join(self.source_folder), dst=os.path.join(self.package_folder, "licenses"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "mariadb-connector-cpp")
        self.cpp_info.set_property("cmake_target_name", "mariadb-connector-cpp::mariadb-connector-cpp")
        self.cpp_info.set_property("pkg_config_name", "libmariadbcpp")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "shlwapi"]
            if self.options.with_ssl == "schannel":
                self.cpp_info.system_libs.append("secur32")

        if self.options.shared:
            self.cpp_info.libs = ["mariadbcpp"]
            if self.settings.os == "Windows":
                self.cpp_info.defines.append("MARIADB_EXPORTED=__declspec(dllimport)")
        else:
            if self.settings.os == "Windows":
                self.cpp_info.libs = ["mariadbcpp-static"]
                self.cpp_info.defines.append("MARIADB_STATIC_LINK")
            else:
                self.cpp_info.libs = ["mariadbcpp"]

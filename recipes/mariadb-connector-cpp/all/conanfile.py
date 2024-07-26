from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import files, get, copy, replace_in_file, collect_libs, rmdir, rm, apply_conandata_patches, export_conandata_patches
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
import os
import glob

required_conan_version = ">=1.53.0"

class MariadbConnectorCppRecipe (ConanFile):
    name = "mariadb-connector-cpp"
    description = "MariaDB Connector/C++ is used to connect applications " \
                  "developed in C++ to MariaDB and MySQL databases."
    license = "LGPL-2.1-or-later"
    topics = ("mariadb", "mysql", "database")
    homepage = "https://mariadb.com/docs/server/connect/programming-languages/cpp"
    url = "https://github.com/conan-io/conan-center-index"

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

    def source(self):
        get (self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.with_ssl = "schannel"

    def validate(self):
        if self.settings.os != "Windows" and self.options.with_ssl == "schannel":
            raise ConanInvalidConfiguration("schannel only supported on Windows")
        if self.options.with_ssl == "gnutls":
            raise ConanInvalidConfiguration("gnutls not yet available in CCI")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        
        tc.variables["WITH_UNIT_TESTS"] = False
        tc.variables["INSTALL_BINDIR"] = "bin"
        tc.variables["INSTALL_LIBDIR"] = "lib"
        tc.variables["INSTALL_PLUGINDIR"] = os.path.join("lib", "plugin").replace("\\", "/")
        tc.variables["USE_SYSTEM_INSTALLED_LIB"] = True
        tc.variables["MARIADB_LINK_DYNAMIC"] = True

        if (self.settings.os == "Windows"):
            tc.variables["CONC_WITH_MSI"] = False
            tc.variables["WITH_MSI"] = False

        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        tc.generate()

    def requirements(self):
        if self.options.with_curl:
            # precompiled mariadb-connector-c accepts only this version of libcurl
            self.requires ("libcurl/8.6.0")
        
        # with_iconv doesn't exists on Windows (Why?)
        self.requires ("mariadb-connector-c/3.3.3", options={
            "dyncol": self.options.dyncol,
            "with_curl": self.options.with_curl,
            "with_ssl": self.options.with_ssl
        })

    def export_sources(self):
        export_conandata_patches(self)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()

        cmake = CMake(self)

        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "COPYING", src=os.path.join(self.package_folder, "share", "doc"), dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join (self.package_folder, "share"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

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

        self.cpp_info.libs = collect_libs(self)
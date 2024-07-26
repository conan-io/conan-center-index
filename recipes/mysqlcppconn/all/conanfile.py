import os
from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, replace_in_file, export_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=1.64.1"

class MysqlCppConnRecipe(ConanFile):
    name = "mysql-concpp"
    version = "9.0.0"
    package_type = "library"
    short_paths = True

    # Optional metadata
    license = "GPL-2.0"
    author = "Hussein Itawi hus@hus.codes"
    url = "https://github.com/husitawi/mysql-conncpp-conan"
    homepage = "https://github.com/mysql/mysql-connector-cpp"
    description = "A MySQL client library for C++ development"
    topics = ("mysql", "sql", "connector", "database", "c++", "cpp")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = { 
               "shared": [True, False], 
               "fPIC": [True, False],
               }

    default_options = { "shared": False, "fPIC": True }

    def export_sources(self):
        export_conandata_patches(self)
    
    def validate(self):
        check_min_cppstd(self, "17")
    
    def requirements(self):
        self.requires("lz4/1.9.4", force=True)
        self.requires("openssl/3.2.2", force=True)
        self.requires("boost/1.85.0", force=True)
        # self.requires("libmysqlclient/8.1.0")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
        
    def _package_folder_dep(self, dep):
        return self.dependencies[dep].package_folder.replace("\\", "/")

    def _include_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.includedirs[0].replace("\\", "/")

    def _lib_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.libdirs[0].replace("\\", "/")
    
    def generate(self):
        tc = CMakeToolchain(self)

        # Random
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        # LZ4 patches
        tc.cache_variables["WITH_LZ4"] = self._package_folder_dep("lz4")
        tc.cache_variables["LZ4_DIR"] = self._package_folder_dep("lz4")
        # Boost patches
        tc.cache_variables["BOOST_DIR"] = self._package_folder_dep("boost")
        # OpenSSL patches
        tc.cache_variables["WITH_SSL"] = self._package_folder_dep("openssl")
        
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()
        
    def _patch_sources(self):
        if not self.options.shared and is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "install_layout.cmake"),
                                "set(LIB_NAME_STATIC \"${LIB_NAME}-mt\")",
                                "set(LIB_NAME_STATIC \"${LIB_NAME_STATIC}-mt\")",
                                strict=False)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
    def package_info(self):
        # Set the VS version
        if self.settings.os == "Windows":
            msvc_toolset_version = self.settings.get_safe("compiler.toolset")
            msvc_version = self.settings.get_safe("compiler.version")

            if msvc_toolset_version:
                vs_version = msvc_toolset_version[1:3]
            elif msvc_version:
                vs_version = msvc_version[:2]
                if vs_version == "18":
                    vs_version = "12"
                elif vs_version == "19":
                    vs_version = "14"
            else:
                self.output.warn("MSVC_TOOLSET_VERSION or MSVC_VERSION not defined")
                vs_version = "unknown"

            self.output.info(f"VS Version: {vs_version}")
            self.vs_version = vs_version
            self.vs = f"vs{vs_version}"
        else:
            self.vs = ""
        
        template_libdirs = ["lib", "lib/debug", "lib64", "lib64/debug"]
        self.cpp_info.libdirs = [f"{lib}/{self.vs}" for lib in template_libdirs]
        self.cpp_info.bindirs = ["lib64", "lib64/debug", "lib", "lib/debug"]
        
        if is_apple_os(self):
            self.cpp_info.system_libs.extend(["resolv"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "resolv"])
        
        target = "concpp-xdevapi" if self.options.shared else "concpp-xdevapi-static"
        target_alias = "concpp" if self.options.shared else "concpp-static"
        
        if self.settings.build_type == "Debug":
            target += "-debug"
            target_alias += "-debug"
        
        # self.cpp_info.set_property("cmake_target_name", f"mysql::{target}")
        self.cpp_info.set_property("cmake_target_name", f"mysql::concpp")
        self.cpp_info.set_property("cmake_target_aliases", [f"mysql::{target_alias}"] )
        
        lib = "mysqlcppconnx" if self.options.shared else "mysqlcppconnx-static"
        if is_msvc(self) and not self.options.shared and is_msvc_static_runtime(self):
            lib += "-mt"
        self.cpp_info.libs = [lib]
        
        if not self.options.shared:
            self.cpp_info.defines = ["MYSQL_STATIC"]
            self.cpp_info.defines = ["STATIC_CONCPP"]
        
        self.cpp_info.set_property("cmake_find_package", "mysql-concpp")
        self.cpp_info.set_property("cmake_find_package_multi", "mysql-concpp")
        self.cpp_info.set_property("cmake_config_file", "mysql-concpp-config.cmake")
        

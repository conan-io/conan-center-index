import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir


required_conan_version = ">=2.0.9"


class LibbaseConan(ConanFile):
    name = "ripper37-libbase"
    description = "Standalone reimplementation of //base module from Chromium"
    license = "MIT"
    url = "https://github.com/RippeR37/libbase"
    homepage = "https://ripper37.github.io/libbase"
    topics = ("Chromium", "base", "net", "multithreading", "async")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "module_net": [True, False],
        "module_win": [True, False],
        "module_wx": [True, False],
    }
    default_options = {
        "fPIC": True,
        "module_net": True,
        "module_win": True,
        "module_wx": False,
    }


    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.module_win

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("glog/0.7.1", transitive_headers=True, transitive_libs=True)
        if self.options.module_net:
            self.requires("libcurl/[>=8.12 <9.0]")
        if self.options.module_wx:
            self.requires("wxwidgets/3.2.6")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os not in ["Windows", "Linux", "Macos"]:
           raise ConanInvalidConfiguration(f"{self.ref} not supported on {self.settings.os}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        # Modules
        tc.cache_variables["LIBBASE_BUILD_MODULE_NET"] = self.options.module_net
        tc.cache_variables["LIBBASE_BUILD_MODULE_WIN"] = self.options.get_safe("module_win", False)
        tc.cache_variables["LIBBASE_BUILD_MODULE_WX"] = self.options.module_wx
        # Internal development options
        tc.cache_variables["LIBBASE_BUILD_EXAMPLES"] = False
        tc.cache_variables["LIBBASE_BUILD_TESTS"] = False
        tc.cache_variables["LIBBASE_BUILD_PERFORMANCE_TESTS"] = False
        tc.cache_variables["LIBBASE_CLANG_TIDY"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        # Core `libbase`
        self.cpp_info.set_property("cmake_file_name", "libbase")
        self.cpp_info.set_property("cmake_target_name", "libbase::libbase")
        self.cpp_info.requires = ["core"]
        self.cpp_info.components["core"].libs = ["libbase"]
        self.cpp_info.components["core"].set_property("cmake_target_name", "libbase::libbase")
        self.cpp_info.components["core"].defines = [f"LIBBASE_IS_{str(self.settings.os).upper()}"]
        self.cpp_info.components["core"].includedirs = ["include/libbase"]
        self.cpp_info.components["core"].requires = ["glog::glog"]

        # Optional components
        components_info = [
            ("net", ["libcurl::libcurl"]),
            ("win", []),
            ("wx",  ["wxwidgets::wxwidgets"]),
        ]
        for comp, deps in components_info:
            if self.options.get_safe(f"module_{comp}", False):
                self.cpp_info.components[comp].libs = [f"libbase_{comp}"]
                self.cpp_info.components[comp].set_property("cmake_target_name", f"libbase::libbase_{comp}")
                self.cpp_info.components[comp].defines = [f"LIBBASE_MODULE_{comp.upper()}"]
                self.cpp_info.components[comp].requires = ["core"] + deps

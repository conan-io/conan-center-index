from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=2.0.5"


class XalanCConan(ConanFile):
    name = "xalan-c"
    description = (
        "Xalan-C++ is a library to transform XML documents using XSLT"
    )
    topics = ("xalan", "XML", "XSLT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://apache.github.io/xalan-c"
    license = "Apache-2.0"

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

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xerces-c/[^3.2.2]", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Because upstream overrides BUILD_SHARED_LIBS as a CACHE variable
        tc.cache_variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        tc.variables["transcoder"] = "default" # icu is currently not supported
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE", "NOTICE"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "XalanC")
        self.cpp_info.set_property("cmake_target_name", "XalanC::XalanC")
        self.cpp_info.set_property("pkg_config_name", "xalan-c")
        self.cpp_info.libs = collect_libs(self)
        
        self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

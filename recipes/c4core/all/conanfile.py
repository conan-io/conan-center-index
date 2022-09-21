from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.51.3"



class C4CoreConan(ConanFile):
    name = "c4core"
    description = (
        "c4core is a library of low-level C++ utilities, written with "
        "low-latency projects in mind."
    )
    license = "MIT",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/biojppm/c4core"
    topics = ("utilities", "low-latency", )
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fast_float": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_fast_float": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_fast_float:
            self.requires("fast_float/3.5.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

        ## clang with libc++ is not supported. It is already fixed since 0.1.9.
        if Version(self.version) <= "0.1.8":
            if self.settings.compiler in ["clang", "apple-clang"] and \
                self.settings.compiler.get_safe("libcxx") == "libc++":
                raise ConanInvalidConfiguration(f"{self.ref} doesn't support clang with libc++")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["C4CORE_WITH_FASTFLOAT"] = bool(self.options.with_fast_float)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.natvis", os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["c4core"]
        if not self.options.with_fast_float:
            self.cpp_info.defines.append("C4CORE_NO_FAST_FLOAT")

        self.cpp_info.set_property("cmake_file_name", "c4core")
        self.cpp_info.set_property("cmake_target_name", "c4core::c4core")

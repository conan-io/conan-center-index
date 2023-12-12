import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.52.0"


class LibCheckConan(ConanFile):
    name = "libcheck"
    description = "A unit testing framework for C"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libcheck/check"
    topics = ("unit", "testing", "framework", "C")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_subunit": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_subunit": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_subunit:
            self.requires("subunit/1.4.0", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CHECK_ENABLE_TESTS"] = False
        tc.variables["ENABLE_MEMORY_LEAKING_TESTS"] = False
        tc.variables["CHECK_ENABLE_TIMEOUT_TESTS"] = False
        tc.variables["HAVE_SUBUNIT"] = self.options.with_subunit
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Do not build the unnecessary target
        disabled_target = "check" if self.options.shared else "checkShared"
        save(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
             f"set_target_properties({disabled_target} PROPERTIES EXCLUDE_FROM_ALL TRUE)\n",
             append=True)


    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.LESSER", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        target = "checkShared" if self.options.shared else "check"
        self.cpp_info.set_property("cmake_file_name", "check")
        self.cpp_info.set_property("cmake_target_name", f"Check::{target}")
        self.cpp_info.set_property("pkg_config_name", "check")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        libsuffix = "Dynamic" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.components["liblibcheck"].libs = [f"check{libsuffix}"]
        if self.options.with_subunit:
            self.cpp_info.components["liblibcheck"].requires.append("subunit::subunit")
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["liblibcheck"].system_libs = ["m", "pthread", "rt"]

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "check"
        self.cpp_info.filenames["cmake_find_package_multi"] = "check"
        self.cpp_info.names["cmake_find_package"] = "Check"
        self.cpp_info.names["cmake_find_package_multi"] = "Check"
        self.cpp_info.components["liblibcheck"].names["cmake_find_package"] = target
        self.cpp_info.components["liblibcheck"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["liblibcheck"].set_property("cmake_target_name", f"Check::{target}")
        self.cpp_info.components["liblibcheck"].set_property("pkg_config_name", "check")

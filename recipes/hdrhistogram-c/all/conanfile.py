from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.52.0"


class HdrhistogramcConan(ConanFile):
    name = "hdrhistogram-c"
    license = ("BSD-2-Clause", "CC0-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HdrHistogram/HdrHistogram_c"
    description = "'C' port of High Dynamic Range (HDR) Histogram"
    topics = ("libraries", "c", "histogram")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/1.2.12")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HDR_HISTOGRAM_BUILD_PROGRAMS"] = False
        tc.variables["HDR_HISTOGRAM_BUILD_SHARED"] = self.options.shared
        tc.variables["HDR_HISTOGRAM_INSTALL_SHARED"] = self.options.shared
        tc.variables["HDR_HISTOGRAM_BUILD_STATIC"] = not self.options.shared
        tc.variables["HDR_HISTOGRAM_INSTALL_STATIC"] = not self.options.shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        target = "hdr_histogram" if self.options.shared else "hdr_histogram_static"
        self.cpp_info.set_property("cmake_file_name", "hdr_histogram")
        self.cpp_info.set_property("cmake_target_name", f"hdr_histogram::{target}")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["hdr_histrogram"].libs = collect_libs(self)
        self.cpp_info.components["hdr_histrogram"].includedirs.append(os.path.join("include", "hdr"))
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["hdr_histrogram"].system_libs = ["m", "rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["hdr_histrogram"].system_libs = ["ws2_32"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "hdr_histogram"
        self.cpp_info.names["cmake_find_package_multi"] = "hdr_histogram"
        self.cpp_info.components["hdr_histrogram"].names["cmake_find_package"] = target
        self.cpp_info.components["hdr_histrogram"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["hdr_histrogram"].set_property("cmake_target_name", f"hdr_histogram::{target}")
        self.cpp_info.components["hdr_histrogram"].requires = ["zlib::zlib"]

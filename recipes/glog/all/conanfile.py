from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class GlogConan(ConanFile):
    name = "glog"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/glog/"
    description = "Google logging library"
    topics = ("conan", "glog", "logging")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gflags": [True, False],
        "with_threads": [True, False],
        "with_unwind": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gflags": True,
        "with_threads": True,
        "with_unwind": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"] or Version(self.version) < "0.5.0":
            del self.options.with_unwind

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_gflags:
            self.options["gflags"].shared = self.options.shared

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        # 0.4.0 requires libunwind unconditionally
        if self.options.get_safe("with_unwind") or (Version(self.version) < "0.5.0" and self.settings.os in ["Linux", "FreeBSD"]):
            self.requires("libunwind/1.6.2")

    def build_requirements(self):
        if Version(self.version) >= "0.6.0":
            self.build_requires("cmake/3.22.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_GFLAGS"] = self.options.with_gflags
        tc.variables["WITH_THREADS"] = self.options.with_threads
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        if Version(self.version) >= "0.5.0":
            tc.variables["WITH_PKGCONFIG"] = True
            if self.settings.os == "Emscripten":
                tc.variables["WITH_SYMBOLIZE"] = False
                tc.variables["HAVE_SYSCALL_H"] = False
                tc.variables["HAVE_SYS_SYSCALL_H"] = False
            else:
                tc.variables["WITH_SYMBOLIZE"] = True
            tc.variables["WITH_UNWIND"] = self.options.get_safe("with_unwind", default=False)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["WITH_GTEST"] = False
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # do not force PIC
        if Version(self.version) <= "0.5.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                  "set_target_properties (glog PROPERTIES POSITION_INDEPENDENT_CODE ON)",
                                  "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glog")
        self.cpp_info.set_property("cmake_target_name", "glog::glog")
        self.cpp_info.set_property("pkg_config_name", "libglog")
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["glog" + postfix]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["dbghelp"]
            self.cpp_info.defines = ["GLOG_NO_ABBREVIATED_SEVERITIES"]
            decl = "__declspec(dllimport)" if self.options.shared else ""
            self.cpp_info.defines.append(f"GOOGLE_GLOG_DLL_DECL={decl}")
        if self.options.with_gflags and not self.options.shared:
            self.cpp_info.defines.extend(["GFLAGS_DLL_DECLARE_FLAG=", "GFLAGS_DLL_DEFINE_FLAG="])

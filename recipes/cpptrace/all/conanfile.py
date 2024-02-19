from conan import ConanFile
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class CpptraceConan(ConanFile):
    name = "cpptrace"
    description = "Simple, portable, and self-contained stacktrace library for C++11 and newer "
    license = ("MIT", "LGPL-2.1-only", "BSD-2-Clause-Views")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jeremy-rifkin/cpptrace"
    topics = ("stacktrace", "backtrace", "stack-trace", "back-trace", "trace", "utilities", "error-handling")
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

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= Version("0.4.0"):
            self.requires("libdwarf/0.9.1")
        else:
            self.requires("libdwarf/0.8.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        if Version(self.version) >= Version("0.3.0"):
            tc.variables["CPPTRACE_USE_EXTERNAL_LIBDWARF"] = True
            tc.variables["CPPTRACE_CONAN"] = True
        else:
            if not self.options.shared:
                tc.variables["CPPTRACE_STATIC"] = True
            tc.variables["CPPTRACE_USE_SYSTEM_LIBDWARF"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Windows" and self.options.shared:
            copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["cpptrace"]

        self.cpp_info.set_property("cmake_module_file_name", "cpptrace")
        self.cpp_info.set_property("cmake_module_target_name", "cpptrace")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("dbghelp")

        if not self.options.shared:
            self.cpp_info.defines.append("CPPTRACE_STATIC_DEFINE")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "CPPTRACE"
        self.cpp_info.filenames["cmake_find_package_multi"] = "cpptrace"
        self.cpp_info.names["cmake_find_package"] = "CPPTRACE"
        self.cpp_info.names["cmake_find_package_multi"] = "cpptrace"

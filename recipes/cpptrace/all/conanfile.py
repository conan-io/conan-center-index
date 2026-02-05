from conan import ConanFile
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.1"

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
        "unwind": ["default", "libunwind"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "unwind": "default",
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
        self.requires("libdwarf/[>=0.11.0 <3]")
        if self.options.unwind == "libunwind":
            self.requires("libunwind/1.8.0", transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "Autoconfig.cmake"),
                        "set(CMAKE_CXX_STANDARD 11)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.variables["CPPTRACE_USE_EXTERNAL_LIBDWARF"] = True
        tc.variables["CPPTRACE_CONAN"] = True
        if self.options.unwind == "libunwind":
            tc.variables["CPPTRACE_UNWIND_WITH_LIBUNWIND"] = True
        tc.cache_variables["CPPTRACE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Windows" and self.options.shared:
            copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

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

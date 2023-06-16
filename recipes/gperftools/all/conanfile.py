import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, get, copy, rm, rmdir

required_conan_version = ">=1.53.0"


class GperftoolsConan(ConanFile):
    name = "gperftools"
    description = "High-performance multi-threaded malloc()"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gperftools/gperftools"
    topics = ("memory", "allocator", "tcmalloc", "google-perftools")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_cpu_profiler": [True, False],
        "build_heap_profiler": [True, False],
        "build_heap_checker": [True, False],
        "build_debugalloc": [True, False],
        "dynamic_sized_delete_support": [True, False],
        "emergency_malloc": [None, True, False],
        "enable_frame_pointers": [True, False],
        "enable_libunwind": [True, False],
        "enable_stacktrace_via_backtrace": [None, True, False],
        "sized_delete": [True, False],
        "tcmalloc_alignment": [None, "ANY"],
        "tcmalloc_pagesize": [None, "ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_cpu_profiler": False,
        "build_heap_profiler": False,
        "build_heap_checker": False,
        "build_debugalloc": False,
        "dynamic_sized_delete_support": False,
        "emergency_malloc": None,
        "enable_frame_pointers": False,
        "enable_libunwind": False,
        "enable_stacktrace_via_backtrace": None,
        "sized_delete": False,
        "tcmalloc_alignment": None,
        "tcmalloc_pagesize": None,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_libunwind:
            self.requires("libunwind/1.6.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GPERFTOOLS_BUILD_STATIC"] = not self.options.shared
        tc.variables["GPERFTOOLS_BUILD_CPU_PROFILER"] = self.options.build_cpu_profiler
        tc.variables["GPERFTOOLS_BUILD_HEAP_PROFILER"] = self.options.build_heap_profiler
        tc.variables["GPERFTOOLS_BUILD_HEAP_CHECKER"] = self.options.build_heap_checker
        tc.variables["GPERFTOOLS_BUILD_DEBUGALLOC"] = self.options.build_debugalloc
        tc.variables["gperftools_dynamic_sized_delete_support"] = self.options.dynamic_sized_delete_support
        tc.variables["gperftools_emergency_malloc"] = self.options.emergency_malloc
        tc.variables["gperftools_enable_frame_pointers"] = self.options.enable_frame_pointers
        tc.variables["gperftools_enable_libunwind"] = self.options.enable_libunwind
        tc.variables["gperftools_enable_stacktrace_via_backtrace"] = self.options.enable_stacktrace_via_backtrace
        tc.variables["gperftools_sized_delete"] = self.options.sized_delete
        tc.variables["gperftools_tcmalloc_alignment"] = self.options.tcmalloc_alignment
        tc.variables["gperftools_tcmalloc_pagesize"] = self.options.tcmalloc_pagesize
        tc.variables["gperftools_build_benchmark"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="COPYING",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder)

    def package_info(self):
        # TODO: should split into components to avoid over-linking
        self.cpp_info.libs = ["tcmalloc_minimal"]
        if self.options.build_debugalloc:
            self.cpp_info.libs.append("tcmalloc_minimal_debug")
        if self.options.build_heap_profiler or self.options.build_heap_checker:
            self.cpp_info.libs.append("tcmalloc")
            if self.options.build_debugalloc:
                self.cpp_info.libs.append("tcmalloc_debug")
        if self.options.build_cpu_profiler:
            self.cpp_info.libs.append("profiler")
            if "tcmalloc" in self.cpp_info.libs:
                self.cpp_info.libs.append("tcmalloc_and_profiler")

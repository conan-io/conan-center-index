import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir

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
        "enable_libunwind": True,
        "enable_stacktrace_via_backtrace": False,
        "sized_delete": False,
        "tcmalloc_alignment": None,
        "tcmalloc_pagesize": None,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _build_minimal(self):
        # Corresponds to the gperftools build_minimal option
        return not (
            self.options.build_cpu_profiler
            or self.options.build_heap_profiler
            or self.options.build_heap_checker
        )

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self._build_minimal:
            # Minimal build does not include stack trace support, so these options are irrelevant
            self.options.rm_safe("enable_libunwind")
            self.options.rm_safe("enable_frame_pointers")
            self.options.rm_safe("enable_stacktrace_via_backtrace")
            self.options.rm_safe("emergency_malloc")
        elif self.options.enable_libunwind:
            # enable_stacktrace_via_backtrace has no effect if libunwind is enabled
            self.options.rm_safe("enable_stacktrace_via_backtrace")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "gperftools recipe does not currently support Windows. Contributions are welcome."
            )

    def requirements(self):
        if self.options.get_safe("enable_libunwind", False):
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
        tc.variables["gperftools_build_minimal"] = self._build_minimal
        if self._build_minimal:
            # No stack trace support will be built
            tc.variables["gperftools_enable_libunwind"] = False
            tc.variables["gperftools_enable_frame_pointers"] = False
            tc.variables["gperftools_enable_stacktrace_via_backtrace"] = False
            tc.variables["gperftools_emergency_malloc"] = False
        else:
            tc.variables["gperftools_enable_libunwind"] = self.options.enable_libunwind
            tc.variables["gperftools_enable_frame_pointers"] = self.options.enable_frame_pointers
            if self.options.get_safe("enable_stacktrace_via_backtrace", False):
                tc.variables[
                    "gperftools_enable_stacktrace_via_backtrace"
                ] = self.options.enable_stacktrace_via_backtrace
            if self.options.emergency_malloc:
                tc.variables["gperftools_emergency_malloc"] = self.options.emergency_malloc
        tc.variables["gperftools_dynamic_sized_delete_support"] = self.options.dynamic_sized_delete_support
        tc.variables["gperftools_sized_delete"] = self.options.sized_delete
        if self.options.tcmalloc_alignment:
            tc.variables["gperftools_tcmalloc_alignment"] = self.options.tcmalloc_alignment
        if self.options.tcmalloc_pagesize:
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

        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.shared:
            # gpreftools builds both static and shared libraries if static is enabled
            rm(self, "*.so", os.path.join(self.package_folder, "lib"))
            rm(self, "*.so.*", os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def _add_component(self, lib):
        self.cpp_info.components[lib].libs = [lib]

    def package_info(self):
        self._add_component("tcmalloc_minimal")
        if self.options.build_debugalloc:
            self._add_component("tcmalloc_minimal_debug")
        if self.options.build_heap_profiler or self.options.build_heap_checker:
            self._add_component("tcmalloc")
            if self.options.build_debugalloc:
                self._add_component("tcmalloc_debug")
        if self.options.build_cpu_profiler:
            self._add_component("profiler")
            if "tcmalloc" in self.cpp_info.components:
                self._add_component("tcmalloc_and_profiler")

        for component in self.cpp_info.components.values():
            if self.settings.os in ["Linux", "FreeBSD"]:
                component.system_libs.extend(["pthread", "m"])
            if self.options.get_safe("enable_libunwind"):
                component.requires.append("libunwind::libunwind")

        # Select the preferred library to link against by default
        main_component = self.cpp_info.components["gperftools"]
        for lib in [
            "tcmalloc_and_profiler",
            "tcmalloc",
            "tcmalloc_debug",
            "tcmalloc_minimal_debug",
            "tcmalloc_minimal",
        ]:
            if lib in self.cpp_info.components:
                main_component.requires = [lib]
                if lib != "tcmalloc_and_profiler" and "profiler" in self.cpp_info.components:
                    main_component.requires.append("profiler")
                break

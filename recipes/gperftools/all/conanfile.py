from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building, check_min_cppstd, stdcpp_library
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.scm import Version
import os

required_conan_version = ">=2"


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
        "enable_aggressive_decommit_by_default": [True, False],
        "enable_frame_pointers": [True, False],
        "enable_large_alloc_report": [True, False],
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
        "enable_aggressive_decommit_by_default": False,
        "enable_frame_pointers": False,
        "enable_large_alloc_report": False,
        "enable_libunwind": True,
        "enable_stacktrace_via_backtrace": False,
        "sized_delete": False,
        "tcmalloc_alignment": None,
        "tcmalloc_pagesize": None,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # INFO: Supports only tcmalloc_minimal on Windows
            # https://github.com/gperftools/gperftools/blob/master/INSTALL#L116
            del self.options.build_cpu_profiler
            del self.options.build_heap_profiler
            del self.options.build_heap_checker
            del self.options.build_debugalloc

    @property
    def _build_minimal(self):
        # Corresponds to the gperftools build_minimal option
        return not (
            self.options.get_safe("build_cpu_profiler")
            or self.options.get_safe("build_heap_profiler")
            or self.options.get_safe("build_heap_checker")
        ) or self.settings.os == "Windows"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self._build_minimal:
            # Minimal build does not include stack trace support, so these options are irrelevant
            self.options.rm_safe("enable_libunwind")
            self.options.rm_safe("enable_frame_pointers")
            self.options.rm_safe("enable_stacktrace_via_backtrace")
            self.options.rm_safe("emergency_malloc")
        elif self.options.get_safe("enable_libunwind"):
            # enable_stacktrace_via_backtrace has no effect if libunwind is enabled
            self.options.rm_safe("enable_stacktrace_via_backtrace")

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(f"{self.ref} does not support gcc < 7.")

    def requirements(self):
        if self.options.get_safe("enable_libunwind", False):
            self.requires("libunwind/[>=1.6.2 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.cache_variables["BUILD_TESTING"] = False
            tc.cache_variables["gperftools_enable_broken_install_targets"] = True
            tc.cache_variables["gperftools_dynamic_sized_delete_support"] = self.options.dynamic_sized_delete_support
            tc.cache_variables["gperftools_enable_large_alloc_report"] = self.options.enable_large_alloc_report
            tc.cache_variables["gperftools_enable_aggressive_decommit_by_default"] = self.options.enable_aggressive_decommit_by_default
            tc.cache_variables["gperftools_sized_delete"] = self.options.sized_delete
            if self.options.get_safe("tcmalloc_alignment"):
                tc.cache_variables["gperftools_tcmalloc_alignment"] = self.options.tcmalloc_alignment
            if self.options.get_safe("tcmalloc_pagesize"):
                tc.cache_variables["gperftools_tcmalloc_pagesize"] = self.options.tcmalloc_pagesize
            tc.generate()
            return

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        args = {}
        args["prefix"] = ""
        args["enable-cpu-profiler"] = self.options.get_safe("build_cpu_profiler", False)
        args["enable-heap-profiler"] = self.options.get_safe("build_heap_profiler", False)
        args["enable-heap-checker"] = self.options.get_safe("build_heap_checker", False)
        args["enable-debugalloc"] = self.options.get_safe("build_debugalloc", False)
        args["enable-minimal"] = self._build_minimal
        args["enable-dynamic-sized-delete-support"] = self.options.get_safe("dynamic_sized_delete_support", False)
        args["enable-sized-delete"] = self.options.get_safe("sized_delete", False)
        args["enable-large-alloc-report"] = self.options.get_safe("enable_large_alloc_report", False)
        args["enable-aggressive-decommit-by-default"] = self.options.get_safe("enable_aggressive_decommit_by_default", False)
        if self._build_minimal:
            # No stack trace support will be built
            args["enable-libunwind"] = False
            args["enable-frame-pointers"] = False
            args["enable-stacktrace-via-backtrace"] = False
            args["enable-emergency-malloc"] = False
        else:
            args["enable-libunwind"] = self.options.get_safe("enable_libunwind", False)
            args["enable-frame-pointers"] = self.options.get_safe("enable_frame_pointers", False)
            args["enable-stacktrace-via-backtrace"] = self.options.get_safe(
                "enable_stacktrace_via_backtrace", False
            )
            args["enable-emergency-malloc"] = self.options.get_safe("emergency_malloc", False)
        args["with-tcmalloc-alignment"] = self.options.get_safe("tcmalloc_alignment", False)
        args["with-tcmalloc-pagesize"] = self.options.get_safe("tcmalloc_pagesize", False)

        for k, v in args.items():
            if v in [True, False]:
                v = "yes" if v else "no"
            if v is not None:
                tc.configure_args.append(f"--{k}={v}")
        tc.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

    def _patch_sources(self):
        makefile_in = os.path.join(self.source_folder, "Makefile.in")
        # Disable building of test programs and benchmark programs
        for pattern in ["noinst_PROGRAMS = ", "TESTS = "]:
            replace_in_file(self, makefile_in, pattern, f"{pattern}\n_{pattern}")
        # Avoid building gtest and bencmark by default (no option)
        replace_in_file(self, makefile_in, "libgtest.la ", "")
        replace_in_file(self, makefile_in, " librun_benchmark.la", "")

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
            copy(self, "*.h", src=os.path.join(self.source_folder, "src", "gperftools"), dst=os.path.join(self.package_folder, "include", "gperftools"))
            if not self.options.shared:
                copy(self, "common.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
                copy(self, "libcommon.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def _add_component(self, lib):
        self.cpp_info.components[lib].libs = [lib]
        self.cpp_info.components[lib].set_property("pkg_config_name", f"lib{lib}")
        if stdcpp_library(self):
            self.cpp_info.components[lib].system_libs.append(stdcpp_library(self))

    def package_info(self):
        self._add_component("tcmalloc_minimal")
        if self.settings.os == "Windows" and not self.options.shared:
            self._add_component("common")
            self.cpp_info.components["tcmalloc_minimal"].requires = ["common"]
        if self.options.get_safe("build_debugalloc"):
            self._add_component("tcmalloc_minimal_debug")
        if self.options.get_safe("build_heap_profiler") or self.options.get_safe("build_heap_checker"):
            self._add_component("tcmalloc")
            if self.options.get_safe("build_debugalloc"):
                self._add_component("tcmalloc_debug")
        if self.options.get_safe("build_cpu_profiler"):
            self._add_component("profiler")
            if "tcmalloc" in self.cpp_info.components:
                self._add_component("tcmalloc_and_profiler")

        for component in self.cpp_info.components.values():
            if self.settings.os in ["Linux", "FreeBSD"]:
                component.system_libs.extend(["pthread", "m"])
                component.cflags.append("-pthread")
                component.cxxflags.append("-pthread")
            elif self.settings.os == "Windows":
                component.system_libs.extend(["Psapi", "Synchronization", "shlwapi"])
                if not self.options.shared:
                    component.defines.append("PERFTOOLS_DLL_DECL=")
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

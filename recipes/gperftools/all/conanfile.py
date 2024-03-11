from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os, XCRun
from conan.tools.build import cross_building, check_min_cppstd, stdcpp_library
from conan.tools.cmake import cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.scm import Version
import os

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

    @property
    def _min_cppstd(self):
        return 11

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
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if Version(self.version) >= "2.11.0" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(f"{self.ref} does not support gcc < 7.")

        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                f"{self.ref} does not currently support Windows. Contributions are welcome."
            )

    def requirements(self):
        if self.options.get_safe("enable_libunwind", False):
            self.requires("libunwind/1.6.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        args = {}
        args["prefix"] = ""
        args["enable-cpu-profiler"] = self.options.build_cpu_profiler
        args["enable-heap-profiler"] = self.options.build_heap_profiler
        args["enable-heap-checker"] = self.options.build_heap_checker
        args["enable-debugalloc"] = self.options.build_debugalloc
        args["enable-minimal"] = self._build_minimal
        args["enable-dynamic-sized-delete-support"] = self.options.dynamic_sized_delete_support
        args["enable-sized-delete"] = self.options.sized_delete
        args["enable-large-alloc-report"] = self.options.enable_large_alloc_report
        args["enable-aggressive-decommit-by-default"] = self.options.enable_aggressive_decommit_by_default
        if self._build_minimal:
            # No stack trace support will be built
            args["enable-libunwind"] = False
            args["enable-frame-pointers"] = False
            args["enable-stacktrace-via-backtrace"] = False
            args["enable-emergency-malloc"] = False
        else:
            args["enable-libunwind"] = self.options.enable_libunwind
            args["enable-frame-pointers"] = self.options.enable_frame_pointers
            args["enable-stacktrace-via-backtrace"] = self.options.get_safe(
                "enable_stacktrace_via_backtrace", False
            )
            args["enable-emergency-malloc"] = self.options.emergency_malloc
        args["with-tcmalloc-alignment"] = self.options.tcmalloc_alignment
        args["with-tcmalloc-pagesize"] = self.options.tcmalloc_pagesize

        # Based on https://github.com/conan-io/conan-center-index/blob/c647b1/recipes/libx264/all/conanfile.py#L94
        if is_apple_os(self) and self.settings.arch == "armv8":
            args["host"] = "aarch64-apple-darwin"
            tc.extra_asflags = ["-arch arm64"]
            tc.extra_ldflags = ["-arch arm64"]
            if self.settings.os != "Macos":
                xcrun = XCRun(self)
                platform_flags = ["-isysroot", xcrun.sdk_path]
                apple_min_version_flag = AutotoolsToolchain(self).apple_min_version_flag
                if apple_min_version_flag:
                    platform_flags.append(apple_min_version_flag)
                tc.extra_asflags.extend(platform_flags)
                tc.extra_cflags.extend(platform_flags)
                tc.extra_ldflags.extend(platform_flags)

        for k, v in args.items():
            if v in [True, False]:
                v = "yes" if v else "no"
            if v is not None:
                tc.configure_args.append(f"--{k}={v}")
        tc.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

    def _patch_sources(self):
        # Disable building of tests and benchmarks in Makefile
        for pattern in ["noinst_PROGRAMS = ", "TESTS = "]:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "Makefile.in"),
                pattern,
                f"{pattern}\n_{pattern}",
            )

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
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
                component.cflags.append("-pthread")
                component.cxxflags.append("-pthread")
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

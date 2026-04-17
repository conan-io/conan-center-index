from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class TracyConan(ConanFile):
    name = "tracy"
    description = "C++ frame profiler"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wolfpld/tracy"
    topics = ("profiler", "performance", "gamedev")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    # Existing CMake tracy options with default value
    _tracy_options = {
        "enable": ([True, False], True),
        "on_demand": ([True, False], False),
        "callstack": ([True, False], False),
        "no_callstack": ([True, False], False),
        "no_callstack_inlines": ([True, False], False),
        "only_localhost": ([True, False], False),
        "no_broadcast": ([True, False], False),
        "only_ipv4": ([True, False], False),
        "no_code_transfer": ([True, False], False),
        "no_context_switch": ([True, False], False),
        "no_exit": ([True, False], False),
        "no_sampling": ([True, False], False),
        "no_verify": ([True, False], False),
        "no_vsync_capture": ([True, False], False),
        "no_frame_image": ([True, False], False),
        "no_system_tracing": ([True, False], False),
        "patchable_nopsleds": ([True, False], False),
        "delayed_init": ([True, False], False),
        "manual_lifetime": ([True, False], False),
        "fibers": ([True, False], False),
        "no_crash_handler": ([True, False], False),
        "timer_fallback": ([True, False], False),
        "libunwind_backtrace": ([True, False], False),
        "symbol_offline_resolve": ([True, False], False),
        "libbacktrace_elf_dynload_support": ([True, False], False),
        "ignore_memory_faults": ([True, False], False),
        "verbose": ([True, False], False),
    }
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        **{k: v[0] for k, v in _tracy_options.items()},
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        **{k: v[1] for k, v in _tracy_options.items()},
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.libunwind_backtrace:
            self.requires("libunwind/1.8.1", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Set all tracy options in the correct form
        # For example, TRACY_NO_EXIT
        for opt in self._tracy_options.keys():
            switch = getattr(self.options, opt)
            opt = f"TRACY_{opt.upper()}"
            tc.variables[opt] = switch
        tc.generate()
        if self.options.libunwind_backtrace:
            deps = PkgConfigDeps(self)
            deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Tracy")
        self.cpp_info.set_property("cmake_target_name", "Tracy::TracyClient")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["tracyclient"].libs = ["TracyClient"]
        if self.options.shared:
            self.cpp_info.components["tracyclient"].defines.append(
                "TRACY_IMPORTS")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["tracyclient"].system_libs.extend([
                "pthread",
                "m"
            ])
        if self.settings.os == "Linux":
            self.cpp_info.components["tracyclient"].system_libs.append("dl")
        if self.settings.os == "Windows":
            self.cpp_info.components["tracyclient"].system_libs.extend([
                "dbghelp",
                "ws2_32"
            ])
        if self.options.libunwind_backtrace:
            self.cpp_info.components["tracyclient"].requires.append("libunwind::libunwind")

        # Starting at 0.12.0, upstream has added an extra "tracy" directory for the include directory
        # include/tracy/tracy/Tracy.hpp
        # but upstream still generates info for including headers as #include <tracy/Tracy.hpp>
        self.cpp_info.components["tracyclient"].includedirs = ['include/tracy']

        # Starting at 0.13.0, upstream introduced a subdirectory in the Runtime/Library/Archive path
        # for all but release type.
        if self.settings.build_type != "Release":
            self.cpp_info.components["tracyclient"].bindirs = ['bin/' + str(self.settings.build_type)]
            self.cpp_info.components["tracyclient"].libdirs = ['lib/' + str(self.settings.build_type)]

        # Tracy CMake adds options set to ON as public
        for opt in self._tracy_options.keys():
            switch = getattr(self.options, opt)
            opt = f"TRACY_{opt.upper()}"
            if switch:
                self.cpp_info.components["tracyclient"].defines.append(opt)

        self.cpp_info.components["tracyclient"].set_property(
            "cmake_target_name", "Tracy::TracyClient")

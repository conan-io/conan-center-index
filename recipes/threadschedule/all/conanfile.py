import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir


required_conan_version = ">=2.0"


class ThreadScheduleConan(ConanFile):
    name = "threadschedule"
    description = "C++17 thread management and scheduling library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Katze719/ThreadSchedule"
    topics = ("threading", "concurrency", "thread-pool", "scheduling", "header-only")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "windows_vista_compat": [True, False],
    }
    default_options = {
        "shared": False,
        "windows_vista_compat": False,
    }

    def config_options(self):
        if self.settings.os != "Windows":
            self.options.rm_safe("windows_vista_compat")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if not self.info.options.shared:
            self.info.settings.clear()

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os not in ("Linux", "Windows"):
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux and Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["THREADSCHEDULE_RUNTIME"] = bool(self.options.shared)
        toolchain.cache_variables["THREADSCHEDULE_BUILD_EXAMPLES"] = False
        toolchain.cache_variables["THREADSCHEDULE_BUILD_TESTS"] = False
        toolchain.cache_variables["THREADSCHEDULE_BUILD_BENCHMARKS"] = False
        toolchain.cache_variables["THREADSCHEDULE_BUILD_DOCS"] = False
        toolchain.cache_variables["THREADSCHEDULE_INSTALL"] = True
        toolchain.cache_variables["THREADSCHEDULE_WINDOWS_VISTA_COMPAT"] = bool(
            self.options.get_safe("windows_vista_compat", False)
        )
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ThreadSchedule")

        headers = self.cpp_info.components["headers"]
        headers.set_property("cmake_target_name", "ThreadSchedule::ThreadSchedule")
        headers.bindirs = []
        headers.libdirs = []
        if self.settings.os == "Linux":
            headers.system_libs = ["pthread", "rt"]
        if self.options.get_safe("windows_vista_compat", False):
            headers.defines = ["THREADSCHEDULE_WINDOWS_VISTA_COMPAT=1"]

        if self.options.shared:
            runtime = self.cpp_info.components["runtime"]
            runtime.set_property("cmake_target_name", "ThreadSchedule::Runtime")
            runtime.libs = ["threadscheduled" if self.settings.build_type == "Debug" else "threadschedule"]
            runtime.requires = ["headers"]
            runtime.defines = ["THREADSCHEDULE_RUNTIME"]

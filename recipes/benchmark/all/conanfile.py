from conan import ConanFile
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.0"


class BenchmarkConan(ConanFile):
    name = "benchmark"
    description = "A microbenchmark support library."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/benchmark"
    topics = ("google", "microbenchmark")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_lto": [True, False],
        "enable_exceptions": [True, False],
        "enable_libpfm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_lto": False,
        "enable_exceptions": True,
        "enable_libpfm": False,
    }

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "1.9.1":
            return 17
        if Version(self.version) >= "1.8.5":
            return 14
        if is_msvc(self):
            return 14
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.enable_libpfm

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, "190")

    def requirements(self):
        if self.options.get_safe("enable_libpfm"):
            self.requires("libpfm4/4.13.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3 <4]")

    def _patch_sources(self):
        replace_in_file(self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "set(CMAKE_CXX_STANDARD",
            "#"
        )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BENCHMARK_ENABLE_TESTING"] = "OFF"
        tc.variables["BENCHMARK_ENABLE_GTEST_TESTS"] = "OFF"
        tc.variables["BENCHMARK_ENABLE_LTO"] = self.options.enable_lto
        tc.variables["BENCHMARK_ENABLE_EXCEPTIONS"] = self.options.enable_exceptions
        tc.variables["BENCHMARK_ENABLE_LIBPFM"] = self.options.get_safe("enable_libpfm", False)
        tc.variables["BENCHMARK_ENABLE_WERROR"] = False
        tc.variables["BENCHMARK_FORCE_WERROR"] = False
        if self.settings.os != "Windows":
            if cross_building(self):
                tc.variables["HAVE_STD_REGEX"] = False
                tc.variables["HAVE_POSIX_REGEX"] = False
                tc.variables["HAVE_STEADY_CLOCK"] = False
            tc.variables["BENCHMARK_USE_LIBCXX"] = self.settings.compiler.get_safe("libcxx") == "libc++"
        else:
            tc.variables["BENCHMARK_USE_LIBCXX"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "benchmark")
        self.cpp_info.set_property("pkg_config_name", "benchmark")

        self.cpp_info.components["_benchmark"].set_property("cmake_target_name", "benchmark::benchmark")
        self.cpp_info.components["_benchmark"].libs = ["benchmark"]
        if not self.options.shared:
            self.cpp_info.components["_benchmark"].defines.append("BENCHMARK_STATIC_DEFINE")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["_benchmark"].system_libs.extend(["pthread", "rt", "m"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["_benchmark"].system_libs.append("shlwapi")
        elif self.settings.os == "SunOS":
            self.cpp_info.components["_benchmark"].system_libs.append("kstat")
        if self.options.get_safe("enable_libpfm"):
            self.cpp_info.components["_benchmark"].requires.append("libpfm4::libpfm4")

        self.cpp_info.components["benchmark_main"].set_property("cmake_target_name", "benchmark::benchmark_main")
        self.cpp_info.components["benchmark_main"].libs = ["benchmark_main"]
        self.cpp_info.components["benchmark_main"].requires = ["_benchmark"]

        # workaround to have all components in CMakeDeps of downstream recipes
        self.cpp_info.set_property("cmake_target_name", "benchmark::benchmark_main")

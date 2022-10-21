from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
import os

required_conan_version = ">=1.51.1"


class PthreadpoolConan(ConanFile):
    name = "pthreadpool"
    description = "pthreadpool is a portable and efficient thread pool " \
                  "implementation. It provides similar functionality to " \
                  "#pragma omp parallel for, but with additional features."
    license = "BSD-2-Clause"
    topics = ("multi-threading", "pthreads", "multi-core", "threadpool")
    homepage = "https://github.com/Maratyszcza/pthreadpool"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sync_primitive": ["default", "condvar", "futex", "gcd", "event"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "sync_primitive": "default",
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fxdiv/cci.20200417")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PTHREADPOOL_LIBRARY_TYPE"] = "default"
        tc.variables["PTHREADPOOL_ALLOW_DEPRECATED_API"] = True
        # TODO: remove str cast in conan 1.53.0 (see https://github.com/conan-io/conan/pull/12086)
        tc.cache_variables["PTHREADPOOL_SYNC_PRIMITIVE"] = str(self.options.sync_primitive)
        tc.variables["PTHREADPOOL_BUILD_TESTS"] = False
        tc.variables["PTHREADPOOL_BUILD_BENCHMARKS"] = False
        tc.cache_variables["FXDIV_SOURCE_DIR"] = "dummy" # this value doesn't really matter, it's just to avoid a download
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}",
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pthreadpool"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc

import os

required_conan_version = ">=1.52.0"

class QuillConan(ConanFile):
    name = "quill"
    description = "Asynchronous Low Latency C++ Logging Library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/odygrd/quill/"
    topics = ("logging", "log", "async")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_bounded_queue": [True, False],
        "with_no_exceptions": [True, False],
        "with_x86_arch": [True, False],
        "with_bounded_blocking_queue": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_bounded_queue": False,
        "with_no_exceptions": False,
        "with_x86_arch": False,
        "with_bounded_blocking_queue": False,
    }

    @property
    def _min_cppstd(self):
        return "17" if Version(self.version) >= "2.0.0" else "14"

    @property
    def _compilers_minimum_versions(self):
        return {
            "14":
                {
                    "gcc": "5",
                    "Visual Studio": "15",
                    "clang": "5",
                    "apple-clang": "10",
                },
            "17":
                {
                    "gcc": "8",
                    "Visual Studio": "16",
                    "clang": "7",
                    "apple-clang": "12",
                },
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if Version(self.version) < "2.8.0":
            del self.options.with_bounded_blocking_queue

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/10.0.0", transitive_headers=True)

    def validate(self):
        supported_archs = ["x86", "x86_64", "armv6", "armv7", "armv7hf", "armv8"]

        if not any(arch in str(self.settings.arch) for arch in supported_archs):
            raise ConanInvalidConfiguration(f"{self.settings.arch} is not supported by {self.ref}")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        compilers_minimum_version = self._compilers_minimum_versions[self._min_cppstd]
        minimum_version = compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        else:
            self.output.warning(f"{self.ref} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")

        if Version(self.version) >= "2.0.0" and \
            self.settings.compiler== "clang" and Version(self.settings.compiler.version).major == "11" and \
            self.settings.compiler.libcxx == "libstdc++":
            raise ConanInvalidConfiguration(f"{self.ref} requires C++ filesystem library, which your compiler doesn't support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def is_quilll_x86_arch(self):
        if not self.options.with_x86_arch:
            return False
        if Version(self.version) < "2.7.0":
            return False
        if self.settings.arch not in ("x86", "x86_64"):
            return False
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            return False
        if is_msvc(self):
            return False
        return True

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QUILL_FMT_EXTERNAL"] = True
        tc.variables["QUILL_ENABLE_INSTALL"] = True

        if Version(self.version) < "2.8.0":
            tc.variables["QUILL_USE_BOUNDED_QUEUE"] = self.options.with_bounded_queue
        else:
            if self.options.with_bounded_queue:
                tc.preprocessor_definitions["QUILL_USE_BOUNDED_QUEUE"] = 1

        tc.variables["QUILL_NO_EXCEPTIONS"] = self.options.with_no_exceptions
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if self.is_quilll_x86_arch():
            if Version(self.version) < "2.8.0":
                tc.variables["QUILL_X86ARCH"] = True
            else:
                tc.preprocessor_definitions["QUILL_X86ARCH"] = 1
            tc.variables["CMAKE_CXX_FLAGS"] = "-mclflushopt"
        if Version(self.version) >= "2.8.0" and self.options.get_safe("with_bounded_blocking_queue"):
            tc.preprocessor_definitions["QUILL_USE_BOUNDED_BLOCKING_QUEUE"] = 1

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # remove bundled fmt
        rmdir(self, os.path.join(self.source_folder, "quill", "quill", "include", "quill", "bundled", "fmt"))
        rmdir(self, os.path.join(self.source_folder, "quill", "quill", "src", "bundled", "fmt"))

        if Version(self.version) >= "2.0.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                """set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_LIST_DIR}/quill/cmake" CACHE STRING "Modules for CMake" FORCE)""",
                """set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH};${CMAKE_CURRENT_LIST_DIR}/quill/cmake")"""
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["quill"]
        self.cpp_info.defines.append("QUILL_FMT_EXTERNAL")
        if self.is_quilll_x86_arch():
            self.cpp_info.defines.append("QUILL_X86ARCH")
            self.cpp_info.cxxflags.append("-mclflushopt")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if Version(self.version) >= "2.0.0" and \
            self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")

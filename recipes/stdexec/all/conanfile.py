from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version

import os


required_conan_version = ">=2.4.0"


class StdexecConan(ConanFile):
    name = "stdexec"
    description = "Reference implementation of the C++26 std::execution (P2300) senders/receivers model"
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIA/stdexec"
    topics = ("execution", "senders", "receivers", "concurrency", "cpp20", "p2300")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_parallel_scheduler": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_parallel_scheduler": True,
    }
    no_copy_source = True

    @property
    def _rapids_cmake_dir(self):
        return os.path.join(self.source_folder, "rapids-cmake").replace("\\", "/")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.with_parallel_scheduler:
            self.package_type = "static-library"
        else:
            self.package_type = "header-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        # the headers do not depend on the settings when the parallel scheduler is not built
        if not self.info.options.with_parallel_scheduler:
            self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)
        # INFO: Upstream only builds and tests GCC 12+, Clang 16+ and MSVC 19.4+ (VS 17.10+)
        minimum_compilers = {
            "gcc": "12",
            "clang": "16",
            "apple-clang": "16",
            "msvc": "194",
            "Visual Studio": "17",
        }
        minimum_version = minimum_compilers.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {self.settings.compiler} {minimum_version} or newer, "
                f"but {self.settings.compiler.version} was detected."
            )

    def build_requirements(self):
        # INFO: upstream CMakeLists.txt requires CMake 3.28
        self.tool_requires("cmake/[>=3.28 <4]")

    def source(self):
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["stdexec"], strip_root=True)
        # upstream pulls rapids-cmake with CMake FetchContent, it is provided as a second source
        get(self, **sources["rapids-cmake"], strip_root=True,
            destination=os.path.join(self.source_folder, "rapids-cmake"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["STDEXEC_BUILD_TESTS"] = False
        tc.cache_variables["STDEXEC_BUILD_EXAMPLES"] = False
        tc.cache_variables["STDEXEC_BUILD_DOCS"] = False
        tc.cache_variables["STDEXEC_INSTALL"] = True
        tc.cache_variables["STDEXEC_BUILD_PARALLEL_SCHEDULER"] = bool(self.options.with_parallel_scheduler)
        # do not let upstream download rapids-cmake (and CPM) at configure time
        tc.cache_variables["FETCHCONTENT_SOURCE_DIR_RAPIDS-CMAKE"] = self._rapids_cmake_dir
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # ConanCenter does not package the CMake config files, the information is provided by CMakeDeps
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "stdexec")

        stdexec = self.cpp_info.components["stdexec"]
        stdexec.set_property("cmake_target_name", "STDEXEC::stdexec")
        stdexec.libdirs = []
        stdexec.bindirs = []
        # same compile definitions as the upstream "stdexec" interface target
        if self.settings.os == "Macos":
            stdexec.defines.append("STDEXEC_ENABLE_LIBDISPATCH")
        if self.settings.os == "Windows":
            stdexec.defines.append("STDEXEC_ENABLE_WINDOWS_THREAD_POOL")
        # same compile options as the upstream "stdexec" interface target
        if self.settings.compiler == "gcc":
            stdexec.cxxflags.extend(["-fcoroutines", "-fconcepts-diagnostics-depth=10"])
        elif self.settings.compiler in ("msvc", "Visual Studio"):
            stdexec.cxxflags.extend(["/Zc:__cplusplus", "/Zc:preprocessor", "/Zc:externConstexpr", "/bigobj"])
        if self.settings.os in ("Linux", "FreeBSD"):
            stdexec.system_libs.append("pthread")

        if self.options.with_parallel_scheduler:
            parallel_scheduler = self.cpp_info.components["parallel_scheduler"]
            parallel_scheduler.set_property("cmake_target_name", "STDEXEC::parallel_scheduler")
            parallel_scheduler.set_property("cmake_target_aliases", ["STDEXEC::system_context"])
            parallel_scheduler.libs = ["parallel_scheduler"]
            parallel_scheduler.requires = ["stdexec"]

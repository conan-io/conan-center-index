from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.microsoft import check_min_vs
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class XnnpackConan(ConanFile):
    name = "xnnpack"
    description = "XNNPACK is a highly optimized library of floating-point " \
                  "neural network inference operators for ARM, WebAssembly, " \
                  "and x86 platforms."
    license = "BSD-3-Clause"
    topics = ("neural-network", "inference", "multithreading", "inference-optimization",
              "matrix-multiplication", "simd")
    homepage = "https://github.com/google/XNNPACK"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "assembly": [True, False],
        "memopt": [True, False],
        "sparse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "assembly": True,
        "memopt": True,
        "sparse": True,
    }

    def export_sources(self):
        copy(self, "xnnpack_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpuinfo/cci.20220228")
        self.requires("fp16/cci.20210320")
        #  https://github.com/google/XNNPACK/blob/ed5f9c0562e016a08b274a4579de5ef500fec134/include/xnnpack.h#L15      
        self.requires("pthreadpool/cci.20210218", transitive_headers=True)
        self.requires("fxdiv/cci.20200417")

    def validate(self):
        check_min_vs(self, 192)
        compiler = self.info.settings.compiler
        compiler_version = Version(compiler.version)
        if (compiler == "gcc" and compiler_version < "6") or \
           (compiler == "clang" and compiler_version < "5"):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support {compiler} {compiler.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.arch == "armv8":
            if self.settings.os == "Linux":
                tc.variables["CONAN_XNNPACK_SYSTEM_PROCESSOR"] = "aarch64"
            else:
                # Not defined by Conan for Apple Silicon. See https://github.com/conan-io/conan/pull/8026
                tc.variables["CONAN_XNNPACK_SYSTEM_PROCESSOR"] = "arm64"
        tc.cache_variables["XNNPACK_LIBRARY_TYPE"] = "shared" if self.options.shared else "static"
        tc.cache_variables["CMAKE_PROJECT_XNNPACK_INCLUDE"] = os.path.join(self.source_folder, "xnnpack_project_include.cmake")
        tc.variables["XNNPACK_ENABLE_ASSEMBLY"] = self.options.assembly
        tc.variables["XNNPACK_ENABLE_MEMOPT"] = self.options.memopt
        tc.variables["XNNPACK_ENABLE_SPARSE"] = self.options.sparse
        tc.variables["XNNPACK_BUILD_TESTS"] = False
        tc.variables["XNNPACK_BUILD_BENCHMARKS"] = False
        tc.variables["XNNPACK_USE_SYSTEM_LIBS"] = True
        # Default fPIC on if it doesn't exist (i.e. for shared library builds)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        # Install only built targets, in this case just the XNNPACK target
        tc.variables["CMAKE_SKIP_INSTALL_ALL_DEPENDENCY"] = True
        # To export symbols for shared msvc
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        # The CMake scripts don't use targets prefixed with `namespace::`
        # so we can coerce CMakeDeps to define the exact target names that
        # are expected. This works in tandem with the file
        # `CMAKE_PROJECT_XNNPACK_INCLUDE` which ensure an early call to 
        # the relevant `find_package`
        deps.set_property("cpuinfo", "cmake_target_name", "cpuinfo")
        deps.set_property("cpuinfo", "cmake_target_aliases", ["clog"] )
        deps.set_property("pthreadpool", "cmake_target_name", "pthreadpool")
        deps.set_property("fp16", "cmake_target_name", "fp16")
        deps.set_property("fxdiv", "cmake_target_name", "fxdiv")
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}",
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="XNNPACK")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["XNNPACK"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

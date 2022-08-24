from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import glob
import os


class XnnpackConan(ConanFile):
    name = "xnnpack"
    description = "XNNPACK is a highly optimized library of floating-point " \
                  "neural network inference operators for ARM, WebAssembly, " \
                  "and x86 platforms."
    license = "BSD-3-Clause"
    topics = ("conan", "xnnpack", "neural-network", "inference", "multithreading",
              "inference-optimization", "matrix-multiplication", "simd")
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

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        compiler = self.settings.compiler
        compiler_version = tools.Version(compiler.version)
        if (compiler == "gcc" and compiler_version < "6") or \
           (compiler == "clang" and compiler_version < "5") or \
           (compiler == "Visual Studio" and compiler_version < "16"):
            raise ConanInvalidConfiguration("xnnpack doesn't support {} {}".format(str(compiler), compiler.version))

    def requirements(self):
        self.requires("cpuinfo/cci.20201217")
        self.requires("fp16/cci.20210320")
        # Note: using newer version of pthreadpool compared to reference cci.20201205
        self.requires("pthreadpool/cci.20210218")

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}",
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("XNNPACK-*")[0]
        os.rename(extracted_dir, self._source_subfolder)
        self._patch_sources()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.arch == "armv8":
            if self.settings.os == "Linux":
                self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
            else:
                # Not defined by Conan for Apple Silicon. See https://github.com/conan-io/conan/pull/8026
                self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "arm64"
        self._cmake.definitions["XNNPACK_LIBRARY_TYPE"] = "shared" if self.options.shared else "static"
        self._cmake.definitions["XNNPACK_ENABLE_ASSEMBLY"] = self.options.assembly
        self._cmake.definitions["XNNPACK_ENABLE_MEMOPT"] = self.options.memopt
        self._cmake.definitions["XNNPACK_ENABLE_SPARSE"] = self.options.sparse
        self._cmake.definitions["XNNPACK_BUILD_TESTS"] = False
        self._cmake.definitions["XNNPACK_BUILD_BENCHMARKS"] = False

        # Default fPIC on if it doesn't exist (i.e. for shared library builds)
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)

        # Use conan dependencies instead of downloading them during configuration
        self._cmake.definitions["XNNPACK_USE_SYSTEM_LIBS"] = True

        # Install only built targets, in this case just the XNNPACK target
        self._cmake.definitions["CMAKE_SKIP_INSTALL_ALL_DEPENDENCY"] = True

        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="XNNPACK")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["XNNPACK"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

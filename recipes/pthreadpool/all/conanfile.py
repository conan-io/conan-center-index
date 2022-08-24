from conan import ConanFile, tools
from conans import CMake
import glob
import os


class PthreadpoolConan(ConanFile):
    name = "pthreadpool"
    description = "pthreadpool is a portable and efficient thread pool " \
                  "implementation. It provides similar functionality to " \
                  "#pragma omp parallel for, but with additional features."
    license = "BSD-2-Clause"
    topics = ("conan", "pthreadpool", "multi-threading", "pthreads",
              "multi-core", "threadpool")
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

    def requirements(self):
        self.requires("fxdiv/cci.20200417")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("pthreadpool-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}",
                              "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PTHREADPOOL_LIBRARY_TYPE"] = "default"
        self._cmake.definitions["PTHREADPOOL_ALLOW_DEPRECATED_API"] = True
        self._cmake.definitions["PTHREADPOOL_SYNC_PRIMITIVE"] = self.options.sync_primitive
        self._cmake.definitions["PTHREADPOOL_BUILD_TESTS"] = False
        self._cmake.definitions["PTHREADPOOL_BUILD_BENCHMARKS"] = False
        self._cmake.definitions["FXDIV_SOURCE_DIR"] = "dummy" # this value doesn't really matter, it's just to avoid a download
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pthreadpool"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]

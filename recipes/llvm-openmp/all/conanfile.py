import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LLVMOpenMpConan(ConanFile):
    name = "llvm-openmp"
    description = ("The OpenMP (Open Multi-Processing) specification "
                   "is a standard for a set of compiler directives, "
                   "library routines, and environment variables that "
                   "can be used to specify shared memory parallelism "
                   "in Fortran and C/C++ programs. This is the LLVM "
                   "implementation.")
    license = "Apache-2.0 WITH LLVM-exception"
    topics = ("conan", "llvm", "openmp", "parallelism")
    homepage = "https://github.com/llvm/llvm-project/tree/master/openmp"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": False}
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _supports_compiler(self):
        supported_compilers_by_os = \
            {"Linux": ["clang", "gcc", "intel"],
             "Macos": ["apple-clang", "clang", "gcc", "intel"],
             "Windows": ["intel"]}
        the_compiler, the_os = self.settings.compiler.value, self.settings.os.value
        return the_compiler in supported_compilers_by_os.get(the_os, [])

    def configure(self):
        if not self._supports_compiler():
            raise ConanInvalidConfiguration("llvm-openmp doesn't support compiler: {} on OS: {}.".
                                            format(self.settings.compiler, self.settings.os))

    def validate(self):
        if (
            tools.Version(self.version) <= "10.0.0"
            and self.settings.os == "Macos"
            and self.settings.arch == "armv8"
        ):
            raise ConanInvalidConfiguration("ARM v8 not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "openmp-{}.src".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        if self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OPENMP_STANDALONE_BUILD"] = True
        self._cmake.definitions["LIBOMP_ENABLE_SHARED"] = self.options.shared
        if self.settings.os == "Linux":
            self._cmake.definitions["OPENMP_ENABLE_LIBOMPTARGET"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        tools.replace_in_file(os.path.join(self._source_subfolder, "runtime/CMakeLists.txt"),
                              "add_subdirectory(test)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.settings.compiler == "clang" or self.settings.compiler == "apple-clang":
            self.cpp_info.cxxflags = ["-Xpreprocessor", "-fopenmp"]
        elif self.settings.compiler == 'gcc':
            self.cpp_info.cxxflags = ["-fopenmp"]
        elif self.settings.compiler == 'intel':
            self.cpp_info.cxxflags = ["/Qopenmp"] if self.settings.os == 'Windows' else ["-Qopenmp"]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "pthread"]

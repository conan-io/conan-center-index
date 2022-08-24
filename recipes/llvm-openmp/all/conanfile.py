from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools
import textwrap

required_conan_version = ">=1.43.0"


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
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        if self.options.shared:
            del self.options.fPIC
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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OPENMP_STANDALONE_BUILD"] = True
        cmake.definitions["LIBOMP_ENABLE_SHARED"] = self.options.shared
        if self.settings.os == "Linux":
            cmake.definitions["OPENMP_ENABLE_LIBOMPTARGET"] = self.options.shared
        cmake.configure()
        return cmake

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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "OpenMP::OpenMP_C": "OpenMP::OpenMP",
                "OpenMP::OpenMP_CXX": "OpenMP::OpenMP"
            }
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenMP")
        self.cpp_info.set_property("cmake_target_name", "OpenMP::OpenMP")
        self.cpp_info.set_property("cmake_target_aliases", ["OpenMP::OpenMP_C", "OpenMP::OpenMP_CXX"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenMP"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenMP"
        self.cpp_info.builddirs.append(os.path.join(self.package_folder, 'lib', 'cmake'))
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        if self.settings.compiler in ("clang", "apple-clang"):
            self.cpp_info.cxxflags = ["-Xpreprocessor", "-fopenmp"]
        elif self.settings.compiler == 'gcc':
            self.cpp_info.cxxflags = ["-fopenmp"]
        elif self.settings.compiler == 'intel':
            self.cpp_info.cxxflags = ["/Qopenmp"] if self.settings.os == 'Windows' else ["-Qopenmp"]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "pthread", "rt"]

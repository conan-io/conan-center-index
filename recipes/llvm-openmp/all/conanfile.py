import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, save
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LLVMOpenMpConan(ConanFile):
    name = "llvm-openmp"
    description = ("The OpenMP (Open Multi-Processing) specification "
                   "is a standard for a set of compiler directives, "
                   "library routines, and environment variables that "
                   "can be used to specify shared memory parallelism "
                   "in Fortran and C/C++ programs. This is the LLVM "
                   "implementation.")
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/llvm/llvm-project/tree/master/openmp"
    topics = ("llvm", "openmp", "parallelism")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _supports_compiler(self):
        supported_compilers_by_os = {
            "Linux": ["clang", "gcc", "intel-cc"],
            "Macos": ["apple-clang", "clang", "gcc", "intel-cc"],
            "Windows": ["intel-cc"],
        }
        the_compiler, the_os = self.settings.compiler.value, self.settings.os.value
        return the_compiler in supported_compilers_by_os.get(the_os, [])

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self._supports_compiler():
            raise ConanInvalidConfiguration("llvm-openmp doesn't support compiler: {} on OS: {}.".
                                            format(self.settings.compiler, self.settings.os))


    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if (
            Version(self.version) <= "10.0.0"
            and is_apple_os(self)
            and self.settings.arch == "armv8"
        ):
            raise ConanInvalidConfiguration("ARM v8 not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPENMP_STANDALONE_BUILD"] = True
        tc.variables["LIBOMP_ENABLE_SHARED"] = self.options.shared
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.variables["OPENMP_ENABLE_LIBOMPTARGET"] = self.options.shared
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self,os.path.join(self.source_folder, "runtime", "CMakeLists.txt"),
                        "add_subdirectory(test)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "OpenMP::OpenMP_C": "OpenMP::OpenMP",
                "OpenMP::OpenMP_CXX": "OpenMP::OpenMP",
            },
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenMP")
        self.cpp_info.set_property("cmake_target_name", "OpenMP::OpenMP")
        self.cpp_info.set_property("cmake_target_aliases", ["OpenMP::OpenMP_C", "OpenMP::OpenMP_CXX"])

        if self.settings.compiler in ("clang", "apple-clang"):
            self.cpp_info.cxxflags = ["-Xpreprocessor", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            self.cpp_info.cxxflags = ["-fopenmp"]
        elif self.settings.compiler == "intel-cc":
            self.cpp_info.cxxflags = ["/Qopenmp"] if self.settings.os == "Windows" else ["-Qopenmp"]
        self.cpp_info.cflags = self.cpp_info.cxxflags
        self.cpp_info.libs = ["omp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread", "rt"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenMP"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenMP"
        self.cpp_info.builddirs.append(os.path.join(self.package_folder, "lib", "cmake"))
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, save, move_folder_contents, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LLVMOpenMpConan(ConanFile):
    name = "llvm-openmp"
    description = ("The OpenMP (Open Multi-Processing) specification is a standard for a set of compiler directives, "
                   "library routines, and environment variables that can be used to specify shared memory parallelism "
                   "in Fortran and C/C++ programs. This is the LLVM implementation.")
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/llvm/llvm-project/blob/main/openmp"
    topics = ("llvm", "openmp", "parallelism")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_libomptarget": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_libomptarget": False,
    }
    options_description = {
        "build_libomptarget": (
            "Build the LLVM OpenMP Offloading Runtime Library (libomptarget) "
            "in addition to the OpenMP Runtime Library (libomp)."
        )
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    @property
    def _version_major(self):
        return Version(self.version).major

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.build_libomptarget and self._version_major >= 13:
            self.requires(f"llvm-core/{self.version}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("llvm-openmp is not compatible with MSVC")
        if self.settings.compiler not in ["apple-clang", "clang", "gcc", "intel-cc"]:
            raise ConanInvalidConfiguration(
                f"{self.settings.compiler} is not supported by this recipe. Contributions are welcome!"
            )
        if self._version_major >= 17:
            if self.settings.compiler.cppstd:
                check_min_cppstd(self, 17)
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++17, which your compiler does not support.")
        if is_apple_os(self) and self.settings.arch == "armv8":
            if self._version_major <= 10:
                raise ConanInvalidConfiguration("ARM v8 not supported")
            if self._version_major != 11 and self.settings.build_type == "Debug":
                # All versions except for v11 crash with a segfault for the simple test_package.cpp test
                raise ConanInvalidConfiguration("Debug mode not supported for ARM v8")

    def build_requirements(self):
        if self._version_major >= 17:
            self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        if self._version_major >= 15:
            get(self, **self.conan_data["sources"][self.version]["openmp"], strip_root=True)
            get(self, **self.conan_data["sources"][self.version]["cmake"], strip_root=True, destination=self.export_sources_folder)
            copy(self, "*.cmake",
                 src=os.path.join(self.export_sources_folder, "Modules"),
                 dst=os.path.join(self.source_folder, "cmake"))
        elif self._version_major == 14:
            # v14 source archives also includes a cmake/ directory in the archive root
            get(self, **self.conan_data["sources"][self.version], destination=self.export_sources_folder)
            move_folder_contents(self, os.path.join(self.export_sources_folder, f"openmp-{self.version}.src"), self.source_folder)
            copy(self, "*.cmake",
                 src=os.path.join(self.export_sources_folder, "cmake", "Modules"),
                 dst=os.path.join(self.source_folder, "cmake"))
        else:
            get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.variables["OPENMP_STANDALONE_BUILD"] = True
        tc.variables["LIBOMP_ENABLE_SHARED"] = self.options.shared
        tc.variables["OPENMP_ENABLE_LIBOMPTARGET"] = self.options.build_libomptarget
        # Do not buidl OpenMP Tools Interface (OMPT)
        tc.variables["LIBOMP_OMPT_SUPPORT"] = False
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "runtime", "CMakeLists.txt"),
                        "add_subdirectory(test)", "")
        if self._version_major == 12:
            # v12 can be built without LLVM includes
            replace_in_file(self, os.path.join(self.source_folder, "libomptarget", "CMakeLists.txt"),
                            "if (NOT LIBOMPTARGET_LLVM_INCLUDE_DIRS)", "if (FALSE)")

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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

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

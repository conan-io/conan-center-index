import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, save, move_folder_contents, rmdir, load, save
from conan.tools.microsoft import is_msvc
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
        copy(self, "*.cmake.in", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.build_libomptarget and self._version_major >= 13:
            self.requires(f"llvm-core/{self.version}")

    def validate(self):
        if self.settings.os == "Windows":
            if not self.options.shared:
                raise ConanInvalidConfiguration("llvm-openmp can only be built as shared on Windows")
            if self._version_major < 17:
                #  fatal error LNK1181: cannot open input file 'build\runtime\src\omp.dll.lib'
                raise ConanInvalidConfiguration(f"{self.ref} build is broken on MSVC for versions < 17")

        if not self._openmp_flags:
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
            if self._version_major >= 12 and self.settings.build_type == "Debug":
                # All versions except for v11 crash with a segfault for the simple test_package.cpp test
                # Might be related to https://github.com/llvm/llvm-project/issues/49923
                raise ConanInvalidConfiguration("Debug mode not supported for ARM v8")

    def build_requirements(self):
        if self._version_major >= 17:
            self.tool_requires("cmake/[>=3.20 <4]")
        if is_msvc(self):
            self.tool_requires("strawberryperl/5.32.1.1")

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
        # Do not build OpenMP Tools Interface (OMPT)
        tc.variables["LIBOMP_OMPT_SUPPORT"] = False
        tc.variables["LIBOMP_INSTALL_ALIASES"] = False
        # The library file incorrectly includes a "lib" prefix on Windows otherwise
        if self.settings.os == "Windows":
            tc.variables["LIBOMP_LIB_NAME"] = "omp"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self._version_major < 17:
            # Fix CMake version and policies not being propagated in linker tests
            replace_in_file(self, os.path.join(self.source_folder, "runtime", "cmake", "LibompCheckLinkerFlag.cmake"),
                            "cmake_minimum_required(",
                            "cmake_minimum_required(VERSION 3.15) #")
            # Ensure sufficient CMake policy version is used for tc.variables
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "cmake_minimum_required(",
                            "cmake_minimum_required(VERSION 3.15) #")
        # Disable tests
        replace_in_file(self, os.path.join(self.source_folder, "runtime", "CMakeLists.txt"),
                        "add_subdirectory(test)", "")
        # v12 can be built without LLVM includes
        if self._version_major == 12:
            replace_in_file(self, os.path.join(self.source_folder, "libomptarget", "CMakeLists.txt"),
                            "if (NOT LIBOMPTARGET_LLVM_INCLUDE_DIRS)", "if (FALSE)")
        # TODO: looks like a bug, should ask upstream
        # The built import lib is named "libomp.dll.lib" otherwise, which also causes install() to fail
        if self._version_major >= 14:
            replace_in_file(self, os.path.join(self.source_folder, "runtime", "src", "CMakeLists.txt"),
                            "set(LIBOMP_GENERATED_IMP_LIB_FILENAME ${LIBOMP_LIB_FILE}${CMAKE_STATIC_LIBRARY_SUFFIX})",
                            "set(LIBOMP_GENERATED_IMP_LIB_FILENAME ${LIBOMP_LIB_NAME}${CMAKE_STATIC_LIBRARY_SUFFIX})")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "openmp", "conan-llvm-openmp-vars.cmake")

    @property
    def _conan1_targets_module_file_rel_path(self):
        return os.path.join("lib", "cmake", "openmp", f"conan-official-{self.name}-targets.cmake")

    @property
    def _openmp_flags(self):
        # Based on https://github.com/Kitware/CMake/blob/v3.28.1/Modules/FindOpenMP.cmake#L104-L135
        if self.settings.compiler == "clang":
            return ["-fopenmp=libomp"]
        elif self.settings.compiler == "apple-clang":
            return ["-Xclang", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            return ["-fopenmp"]
        elif self.settings.compiler == "intel-cc":
            return ["-Qopenmp"]
        elif self.settings.compiler == "sun-cc":
            return ["-xopenmp"]
        elif is_msvc(self):
            return ["-openmp:llvm"]
        return None

    @property
    def _system_libs(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            return ["m", "dl", "pthread", "rt"]
        return []

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        cmake_module = load(self, os.path.join(self.export_sources_folder, "cmake", "conan-llvm-openmp-vars.cmake.in"))
        cmake_module = cmake_module.replace("@OpenMP_FLAGS@", " ".join(self._openmp_flags))
        cmake_module = cmake_module.replace("@OpenMP_LIB_NAMES@", ";".join(["omp"] + self._system_libs))
        save(self, os.path.join(self.package_folder, self._module_file_rel_path), cmake_module)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._conan1_targets_module_file_rel_path),
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

    def package_info(self):
        # Match FindOpenMP.cmake module provided by CMake
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenMP")
        self.cpp_info.set_property("cmake_target_name", "OpenMP::OpenMP")
        self.cpp_info.set_property("cmake_target_aliases", ["OpenMP::OpenMP_C", "OpenMP::OpenMP_CXX"])

        self.cpp_info.libs = ["omp"]
        self.cpp_info.system_libs = self._system_libs
        self.cpp_info.cflags = self._openmp_flags
        self.cpp_info.cxxflags = self._openmp_flags

        self.cpp_info.builddirs.append(os.path.join(self.package_folder, "lib", "cmake", "openmp"))
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenMP"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenMP"
        self.cpp_info.builddirs.append(os.path.join(self.package_folder, "lib", "cmake"))
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path, self._conan1_targets_module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path, self._conan1_targets_module_file_rel_path]

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches, save
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.build import cross_building
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.55.0"


class ArmadilloConan(ConanFile):
    name = "armadillo"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://arma.sourceforge.net"
    description = "Armadillo is a high quality C++ library for linear algebra and scientific computing, aiming towards a good balance between speed and ease of use."
    topics = (
        "linear algebra",
        "scientific computing",
        "matrix",
        "vector",
        "math",
        "blas",
        "lapack",
        "mkl",
        "hdf5",
    )
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_blas": [
            False,
            "openblas",
            "intel_mkl",
            "system_blas",
            "system_flexiblas",
            "framework_accelerate",
        ],
        "use_lapack": [
            False,
            "openblas",
            "intel_mkl",
            "system_lapack",
            "system_atlas",
            "framework_accelerate",
        ],
        "use_hdf5": [True, False],
        "use_superlu": [False, "system_superlu"],
        "use_extern_rng": [True, False],
        "use_arpack": [False, "system_arpack"],
        "use_wrapper": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_blas": "openblas",
        "use_lapack": "openblas",
        "use_hdf5": True,
        "use_superlu": False,
        "use_extern_rng": False,
        "use_arpack": False,
        "use_wrapper": False,
    }
    # Values that must be set for multiple options to be valid
    _co_dependencies = {
        "intel_mkl": [
            "use_blas",
            "use_lapack",
        ],
        "framework_accelerate": [
            "use_blas",
            "use_lapack",
        ],
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os == "Macos":
            # Macos will default to Accelerate framework
            self.options.use_blas = "framework_accelerate"
            self.options.use_lapack = "framework_accelerate"

        # According with the CMakeLists file in armadillo, MinGW doesn't correctly handle thread_local.
        # If any of MINGW, MSYS, CYGWIN or MSVC are True in during cmake configure, the ARMA_USE_EXTERN_RNG option will be set to false.
        # Therefore, in these cases we remove the `use_extern_rng` option in conan
        if self.settings.os == "Windows":
            del self.options.use_extern_rng

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if self.options.use_blas == "openblas":
            self.options["openblas"].build_lapack = (
                self.options.use_lapack == "openblas"
            )

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

        if self.settings.os != "Macos" and (
            self.options.use_blas == "framework_accelerate"
            or self.options.use_lapack == "framework_accelerate"
        ):
            raise ConanInvalidConfiguration(
                "framework_accelerate can only be used on Macos"
            )

        if self.options.use_hdf5 and Version(self.version) > "12" and cross_building(self):
            raise ConanInvalidConfiguration(
                "Armadillo does not support cross building with hdf5. Set use_hdf5=False and try again."
            )

        for value, options in self._co_dependencies.items():
            options_without_value = [
                x for x in options if getattr(self.options, x) != value
            ]
            if options_without_value and (len(options) != len(options_without_value)):
                raise ConanInvalidConfiguration(
                    "Options {} must all be set to '{}' to use this feature. To fix this, set option {} to '{}'.".format(
                        ", ".join(options),
                        value,
                        ", ".join(options_without_value),
                        value,
                    )
                )

        if (
            self.options.use_lapack == "openblas"
            and self.options.use_blas != "openblas"
        ):
            raise ConanInvalidConfiguration(
                "OpenBLAS can only provide LAPACK functionality when also providing BLAS functionality. Set use_blas=openblas and try again."
            )

        deprecated_opts = list(
            set(
                [
                    opt
                    for opt in [
                        str(self.options.use_blas),
                        str(self.options.use_lapack),
                    ]
                    if "system" in opt
                ]
            )
        )

        for opt in deprecated_opts:
            self.output.warning(
                f"DEPRECATION NOTICE: Value {opt} uses armadillo's default dependency search and will be replaced when this package becomes available in ConanCenter"
            )

        # Ignore use_extern_rng when the option has been removed
        if self.options.use_wrapper and not self.options.get_safe("use_extern_rng", True):
            raise ConanInvalidConfiguration(
                "The wrapper requires the use of an external RNG. Set use_extern_rng=True and try again."
            )

        if not self.options.shared and self.options.use_wrapper:
            raise ConanInvalidConfiguration("Building the armadillo run-time wrapper library requires armadillo/*:shared=True")

    def requirements(self):
        # Optional requirements
        # TODO: "atlas/3.10.3" # Pending https://github.com/conan-io/conan-center-index/issues/6757
        # TODO: "superlu/5.2.2" # Pending https://github.com/conan-io/conan-center-index/issues/6756
        # TODO: "arpack/1.0" # Pending https://github.com/conan-io/conan-center-index/issues/6755
        # TODO: "flexiblas/3.0.4" # Pending https://github.com/conan-io/conan-center-index/issues/6827

        # The armadillo library no longer takes any responsibility for linking hdf5 as of v12.x. This means
        # it will have to be linked manually by consumers if desired.
        # See https://gitlab.com/conradsnicta/armadillo-code/-/issues/227 for more information.
        if self.options.use_hdf5 and Version(self.version) < "12":
            # Use the conan dependency if the system lib isn't being used
            # Libraries not required to be propagated transitively when the armadillo run-time wrapper is used
            self.requires("hdf5/1.14.3", transitive_headers=True, transitive_libs=not self.options.use_wrapper)

        if self.options.use_blas == "openblas":
            # Libraries not required to be propagated transitively when the armadillo run-time wrapper is used
            self.requires("openblas/0.3.25", transitive_libs=not self.options.use_wrapper)
        if (
            self.options.use_blas == "intel_mkl"
            and self.options.use_lapack == "intel_mkl"
        ):
            # Consumers can override this requirement with their own
            # by using self.requires("intel-mkl/version@user/channel, override=True)
            # in their consumer conanfile.py
            if (
                self.options.use_blas == "intel_mkl"
                or self.options.use_lapack == "intel_mkl"
            ):
                self.output.warning(
                    "The intel-mkl package does not exist in CCI. To use an Intel MKL package, override this requirement with your own recipe."
                )
            self.requires("intel-mkl/2021.4")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ARMA_USE_LAPACK"] = self.options.use_lapack
        tc.variables["ARMA_USE_BLAS"] = self.options.use_blas
        tc.variables["ARMA_USE_ATLAS"] = self.options.use_lapack == "system_atlas"
        tc.variables["ARMA_USE_HDF5"] = self.options.use_hdf5
        tc.variables["ARMA_USE_HDF5_CMAKE"] = self.options.use_hdf5
        tc.variables["ARMA_USE_ARPACK"] = self.options.use_arpack
        tc.variables["ARMA_USE_EXTERN_RNG"] = self.options.get_safe("use_exern_rng", default=False)
        tc.variables["ARMA_USE_SUPERLU"] = self.options.use_superlu
        tc.variables["ARMA_USE_WRAPPER"] = self.options.use_wrapper
        tc.variables["ARMA_USE_ACCELERATE"] = (
            self.options.use_blas == "framework_accelerate"
            or self.options.use_lapack == "framework_accelerate"
        ) and self.settings.os == "Macos"
        tc.variables["DETECT_HDF5"] = self.options.use_hdf5
        tc.variables["USE_OPENBLAS"] = (self.options.use_blas == "openblas")
        tc.variables["USE_MKL"] = self.options.use_blas == "intel_mkl" and self.options.use_lapack == "intel_mkl"
        tc.variables["USE_SYSTEM_LAPACK"] = self.options.use_lapack == "system_lapack"
        tc.variables["USE_SYSTEM_BLAS"] = (self.options.use_blas == "system_blas")
        tc.variables["USE_SYSTEM_ATLAS"] = self.options.use_lapack == "system_atlas"
        tc.variables["USE_SYSTEM_HDF5"] = False
        tc.variables["USE_SYSTEM_ARPACK"] = self.options.use_arpack
        tc.variables["USE_SYSTEM_SUPERLU"] = self.options.use_superlu
        tc.variables["USE_SYSTEM_OPENBLAS"] = False
        tc.variables["USE_SYSTEM_FLEXIBLAS"] = self.options.use_blas == "system_flexiblas"
        tc.variables["ALLOW_FLEXIBLAS_LINUX"] = self.options.use_blas == "system_flexiblas" and self.settings.os == "Linux"
        tc.variables["ALLOW_OPENBLAS_MACOS"] = self.options.use_blas == "openblas" and self.settings.os == "Macos"
        tc.variables["OPENBLAS_PROVIDES_LAPACK"] = self.options.use_lapack == "openblas"
        tc.variables["ALLOW_BLAS_LAPACK_MACOS"] = self.options.use_blas != "framework_accelerate"
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_SMOKE_TEST"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            filename="f{self.name}-{self.version}.tar.xz"
        )

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _get_arma_version_name(self):
        version_file = os.path.join(self.source_folder, "include", "armadillo_bits", "arma_version.hpp")
        with open(version_file, "r") as f:
            for line in f:
                if "ARMA_VERSION_NAME" in line:
                    return line.split("\"")[-2].strip()
        return ""

    @property
    def _module_vars_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent(f"""\
            set(ARMADILLO_FOUND TRUE)
            if(DEFINED Armadillo_INCLUDE_DIRS)
                set(ARMADILLO_INCLUDE_DIRS ${{Armadillo_INCLUDE_DIRS}})
            endif()
            if(DEFINED Armadillo_LIBRARIES)
                set(ARMADILLO_LIBRARIES ${{Armadillo_LIBRARIES}})
            endif()
            set(ARMADILLO_VERSION_MAJOR "{Version(self.version).major}")
            set(ARMADILLO_VERSION_MINOR "{Version(self.version).minor}")
            set(ARMADILLO_VERSION_PATCH "{Version(self.version).patch}")
            if(DEFINED Armadillo_VERSION_STRING)
                set(ARMADILLO_VERSION_STRING ${{Armadillo_VERSION_STRING}})
            else()
                set(ARMADILLO_VERSION_STRING "${{ARMADILLO_VERSION_MAJOR}}.${{ARMADILLO_VERSION_MINOR}}.${{ARMADILLO_VERSION_PATCH}}")
            endif()
            set(ARMADILLO_VERSION_NAME "{self._get_arma_version_name}")
        """)
        save(self, module_file, content)

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "NOTICE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        self._create_cmake_module_variables(os.path.join(self.package_folder, self._module_vars_rel_path))


    def package_info(self):
        self.cpp_info.libs = ["armadillo"]
        self.cpp_info.set_property("pkg_config_name", "armadillo")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Armadillo")
        self.cpp_info.set_property("cmake_target_name", "Armadillo::Armadillo")
        self.cpp_info.set_property("cmake_target_aliases", ["armadillo", "armadillo::armadillo"])
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_rel_path])

        # Remove when cmake_find_package and pkg_config generators are no
        # longer supported
        self.cpp_info.names["pkg_config"] = "armadillo"
        self.cpp_info.names["cmake_find_package"] = "Armadillo"
        self.cpp_info.names["cmake_find_package_multi"] = "Armadillo"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_vars_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_vars_rel_path]

        if self.options.get_safe("use_extern_rng"):
            self.cpp_info.defines.append("ARMA_USE_EXTERN_RNG")

        if self.settings.build_type == "Release":
            self.cpp_info.defines.append("ARMA_NO_DEBUG")

        # The wrapper library links everything together. If disabled, system libs must be
        # linked manually
        if not self.options.use_wrapper:
            self.cpp_info.defines.append("ARMA_DONT_USE_WRAPPER")
            if self.options.use_blas == "framework_accelerate":
                self.cpp_info.frameworks.append("Accelerate")

        if self.options.use_hdf5:
            self.cpp_info.defines.append("ARMA_USE_HDF5")
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_HDF5")

        if self.options.use_blas:
            self.cpp_info.defines.append("ARMA_USE_BLAS")
            if self.options.use_blas == "system_blas" and not self.options.use_wrapper:
                self.cpp_info.system_libs.extend(["blas"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_BLAS")

        if self.options.use_lapack:
            self.cpp_info.defines.append("ARMA_USE_LAPACK")
            if (
                self.options.use_lapack == "system_lapack"
                and not self.options.use_wrapper
            ):
                self.cpp_info.system_libs.extend(["lapack"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_LAPACK")

        if self.options.use_arpack:
            self.cpp_info.defines.append("ARMA_USE_ARPACK")
            if not self.options.use_wrapper:
                self.cpp_info.system_libs.extend(["arpack"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_ARPACK")

        if self.options.use_superlu:
            self.cpp_info.defines.append("ARMA_USE_SUPERLU")
            if not self.options.use_wrapper:
                self.cpp_info.system_libs.extend(["superlu"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_SUPERLU")

        if self.options.use_lapack == "system_atlas":
            self.cpp_info.defines.append("ARMA_USE_ATLAS")
            if not self.options.use_wrapper:
                self.cpp_info.system_libs.extend(["atlas"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_ATLAS")

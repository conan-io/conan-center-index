from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


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
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # These are options exposed by armadillo_bits/config.hpp
        "ARMA_USE_LAPACK": [True, False],
        "ARMA_USE_BLAS": [True, False],
        "ARMA_USE_ATLAS": [True, False],
        "ARMA_USE_HDF5": [True, False],
        "ARMA_USE_ARPACK": [True, False],
        "ARMA_USE_EXTERN_RNG": [True, False],
        "ARMA_USE_SUPERLU": [True, False],
        "ARMA_USE_WRAPPER": [True, False],
        "ARMA_USE_ACCELERATE": [True, False],  # Use system accelerate framework.
        # These are the options that the armadillo CMakeLists exposes
        "ALLOW_FLEXIBLAS_LINUX": [True, False],
        "ALLOW_OPENBLAS_MACOS": [True, False],
        "ALLOW_BLAS_LAPACK_MACOS": [True, False],
        # These are options unique to this recipe
        # Optional dependencies
        "USE_OPENBLAS": [True, False],  # Use conan OpenBLAS package
        # System dependency overrides
        "USE_SYSTEM_LAPACK": [True, False],
        "USE_SYSTEM_BLAS": [True, False],
        "USE_SYSTEM_ATLAS": [True, False],
        "USE_SYSTEM_HDF5": [True, False],
        "USE_SYSTEM_ARPACK": [True, False],
        "USE_SYSTEM_SUPERLU": [True, False],
        "USE_SYSTEM_OPENBLAS": [True, False],
        "USE_SYSTEM_FLEXIBLAS": [True, False],
        "USE_SYSTEM_MKL": [True, False],
        "MKL_LIBRARY_PATH": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # These are options exposed by armadillo_bits/config.hpp
        "ARMA_USE_LAPACK": False,
        "ARMA_USE_BLAS": True,
        "ARMA_USE_ATLAS": False,
        "ARMA_USE_HDF5": True,
        "ARMA_USE_ARPACK": False,
        "ARMA_USE_EXTERN_RNG": False,
        "ARMA_USE_SUPERLU": False,
        "ARMA_USE_WRAPPER": False,
        "ARMA_USE_ACCELERATE": False,  # Use system accelerate framework.
        # These are the options that the armadillo CMakeLists exposes
        "ALLOW_FLEXIBLAS_LINUX": False,
        "ALLOW_OPENBLAS_MACOS": False,
        "ALLOW_BLAS_LAPACK_MACOS": False,
        # These are options unique to this recipe
        # Optional dependencies
        "USE_OPENBLAS": True,  # Use conan OpenBLAS package
        # System dependency overrides
        "USE_SYSTEM_LAPACK": False,
        "USE_SYSTEM_BLAS": False,
        "USE_SYSTEM_ATLAS": False,
        "USE_SYSTEM_HDF5": False,
        "USE_SYSTEM_ARPACK": False,
        "USE_SYSTEM_SUPERLU": False,
        "USE_SYSTEM_OPENBLAS": False,
        "USE_SYSTEM_FLEXIBLAS": False,
        "USE_SYSTEM_MKL": False,
        "MKL_LIBRARY_PATH": "",
    }
    # Options that have a dependency on a specific operating system
    os_dependencies = {
        "ALLOW_FLEXIBLAS_LINUX": "Linux",
        "ALLOW_BLAS_LAPACK_MACOS": "Macos",
        "ALLOW_OPENBLAS_MACOS": "Macos",
    }
    # Options that require another option to be set to be valid
    opt_dependencies = {
        "Macos": {
            "USE_OPENBLAS": [
                "ALLOW_OPENBLAS_MACOS",
            ],
            "USE_SYSTEM_BLAS": [
                "ALLOW_BLAS_LAPACK_MACOS",
            ],
            "USE_SYSTEM_LAPACK": [
                "ALLOW_BLAS_LAPACK_MACOS",
            ],
        },
        "Linux": {
            "USE_SYSTEM_FLEXIBLAS": [
                "ALLOW_FLEXIBLAS_LINUX",
            ],
        },
        "Windows": {},
        "all": {
            "ARMA_USE_LAPACK": ["ARMA_USE_BLAS"],
            "USE_SYSTEM_LAPACK": ["ARMA_USE_LAPACK"],
            "USE_SYSTEM_BLAS": ["ARMA_USE_BLAS"],
            "USE_SYSTEM_ATLAS": ["ARMA_USE_ATLAS"],
            "USE_SYSTEM_ARPACK": ["ARMA_USE_ARPACK"],
            "USE_SYSTEM_SUPERLU": ["ARMA_USE_SUPERLU"],
            "USE_SYSTEM_HDF5": ["ARMA_USE_HDF5"],
            "MKL_LIBRARY_PATH": ["USE_SYSTEM_MKL"],
        },
    }
    # Options that are mutually exclusive
    exclusions = {
        "blas": [
            "USE_OPENBLAS",
            "USE_SYSTEM_OPENBLAS",
            "USE_SYSTEM_MKL",
            "USE_SYSTEM_FLEXIBLAS",
            "USE_SYSTEM_BLAS",
            "ARMA_USE_ACCELERATE",
        ],
        "lapack": [
            "USE_SYSTEM_LAPACK",
            "USE_SYSTEM_ATLAS",
            "USE_SYSTEM_MKL",
            "ARMA_USE_ACCELERATE",
        ],
    }
    exports_sources = "CMakeLists.txt"
    generators = (
        "cmake",
        "cmake_find_package",
    )
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os == "Macos":
            # Macos will default to Accelerate framework
            self.options.USE_OPENBLAS = False
            self.options.ARMA_USE_LAPACK = True
            self.options.ARMA_USE_ACCELERATE = True
        if self.settings.os != "Macos":
            self.options.ARMA_USE_ACCELERATE = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        # Use default MKL path or throw error if no default path exists
        if self.options.USE_SYSTEM_MKL and not self.options.MKL_LIBRARY_PATH:
            if self.settings.os == "Linux":
                self.options.MKL_LIBRARY_PATH = "/opt/intel/mkl/lib/intel64"
            elif self.settings.os == "Windows":
                self.options.MKL_LIBRARY_PATH = (
                    "C:/IntelSWTools/compilers_and_libraries/windows/mkl/lib/intel64"
                )
            else:
                raise ConanInvalidConfiguration(
                    f"A default MKL_LIBRARY_PATH value for your operating system is not available. Please specify a value for MKL_LIBRARY_PATH"
                )
        # If no BLAS package has been specified, OpenBLAS will be the default
        if (
            self.options.ARMA_USE_BLAS
            and not self.options.USE_OPENBLAS
            and not self.options.USE_SYSTEM_OPENBLAS
            and not self.options.USE_SYSTEM_BLAS
        ):
            blas_conflicts = [
                x for x in self.exclusions["blas"] if getattr(self.options, x)
            ]
            if (
                (
                    (
                        self.settings.os == "Macos"
                        and self.options.ALLOW_BLAS_LAPACK_MACOS
                        and self.options.ALLOW_OPENBLAS_MACOS
                    )
                    or self.settings.os != "Macos"
                )
                and self.options.ARMA_USE_BLAS
                and not blas_conflicts
            ):
                self.options.USE_OPENBLAS = True
        if self.options.ALLOW_BLAS_LAPACK_MACOS:
            self.options.ARMA_USE_ACCELERATE = False

    def validate(self):
        tools.check_min_cppstd(self, "11")
        # Iterate over dependency maps to confirm requirements are met
        for option, dependency in self.os_dependencies.items():
            if getattr(self.options, option) and self.settings.os != dependency:
                raise ConanInvalidConfiguration(
                    f"Option {option} can only be enabled on {dependency} operating systems"
                )
        # Optional option co-depdendencies
        for platform, opts in self.opt_dependencies.items():
            if platform == "all" or platform == self.settings.os:
                for option, dependencies in opts.items():
                    dependencies_in_error = [
                        dependency
                        for dependency in dependencies
                        if not getattr(self.options, dependency)
                    ]
                    if getattr(self.options, option) and dependencies_in_error:
                        raise ConanInvalidConfiguration(
                            "Option {option} cannot be enabled without enabling {missing}".format(
                                option=option, missing=", ".join(dependencies_in_error)
                            )
                        )
        # Mutually exclusive options
        for category, incompatible_opts in self.exclusions.items():
            conflicts = [x for x in incompatible_opts if getattr(self.options, x)]
            if len(conflicts) > 1:
                raise ConanInvalidConfiguration(
                    "The following options are in conflict: {conflict}. Resolve this conflict by ensuring only one of these options is enabled and try again.".format(
                        conflict=", ".join(conflicts)
                    )
                )
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.output.warn(
                "Building a shared library with MSVC is not supported. This may not be successful."
            )

    def requirements(self):
        # Optional requirements
        openblas = "openblas/0.3.15"
        hdf5 = "hdf5/1.12.0"
        # atlas = "atlas/3.10.3" # Pending https://github.com/conan-io/conan-center-index/issues/6757
        # superlu = "superlu/5.2.2" # Pending https://github.com/conan-io/conan-center-index/issues/6756
        # arpack = "arpack/1.0" # Pending https://github.com/conan-io/conan-center-index/issues/6755
        # flexiblas = "flexiblas/3.0.4" # Pending https://github.com/conan-io/conan-center-index/issues/6827

        if self.options.ARMA_USE_HDF5 and not self.options.USE_SYSTEM_HDF5:
            # Use the conan dependency if the system lib isn't being used
            self.requires(hdf5)
            self.options["hdf5"].shared = self.options.shared

        if self.options.USE_OPENBLAS:
            self.requires(openblas)
            # Note that if you're relying on this to build LAPACK, you _must_ have
            # a fortran compiler installed. If you don't, OpenBLAS will build successfully but
            # without LAPACK support, which isn't obvious.
            # This can be achieved by setting the FC environment variable in your conan profile
            self.options["openblas"].build_lapack = (
                self.options.ARMA_USE_LAPACK and not self.options.USE_SYSTEM_LAPACK
            )
            self.options["openblas"].shared = self.options.shared

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ARMA_USE_LAPACK"] = self.options.ARMA_USE_LAPACK
        self._cmake.definitions["ARMA_USE_BLAS"] = self.options.ARMA_USE_BLAS
        self._cmake.definitions["ARMA_USE_ATLAS"] = self.options.ARMA_USE_ATLAS
        self._cmake.definitions["ARMA_USE_HDF5"] = self.options.ARMA_USE_HDF5
        self._cmake.definitions["ARMA_USE_ARPACK"] = self.options.ARMA_USE_ARPACK
        self._cmake.definitions[
            "ARMA_USE_EXTERN_RNG"
        ] = self.options.ARMA_USE_EXTERN_RNG
        self._cmake.definitions["ARMA_USE_SUPERLU"] = self.options.ARMA_USE_SUPERLU
        self._cmake.definitions["ARMA_USE_WRAPPER"] = self.options.ARMA_USE_WRAPPER
        self._cmake.definitions[
            "ARMA_USE_ACCELERATE"
        ] = self.options.ARMA_USE_ACCELERATE
        self._cmake.definitions["DETECT_HDF5"] = self.options.ARMA_USE_HDF5
        self._cmake.definitions["USE_OPENBLAS"] = self.options.USE_OPENBLAS
        self._cmake.definitions["USE_SYSTEM_LAPACK"] = self.options.USE_SYSTEM_LAPACK
        self._cmake.definitions["USE_SYSTEM_BLAS"] = self.options.USE_SYSTEM_BLAS
        self._cmake.definitions["USE_SYSTEM_ATLAS"] = self.options.USE_SYSTEM_ATLAS
        self._cmake.definitions["USE_SYSTEM_HDF5"] = self.options.USE_SYSTEM_HDF5
        self._cmake.definitions["USE_SYSTEM_ARPACK"] = self.options.USE_SYSTEM_ARPACK
        self._cmake.definitions["USE_SYSTEM_SUPERLU"] = self.options.USE_SYSTEM_SUPERLU
        self._cmake.definitions[
            "USE_SYSTEM_OPENBLAS"
        ] = self.options.USE_SYSTEM_OPENBLAS
        self._cmake.definitions[
            "USE_SYSTEM_FLEXIBLAS"
        ] = self.options.USE_SYSTEM_FLEXIBLAS
        self._cmake.definitions["USE_SYSTEM_MKL"] = self.options.USE_SYSTEM_MKL
        self._cmake.definitions[
            "ALLOW_FLEXIBLAS_LINUX"
        ] = self.options.ALLOW_FLEXIBLAS_LINUX
        self._cmake.definitions[
            "ALLOW_OPENBLAS_MACOS"
        ] = self.options.ALLOW_OPENBLAS_MACOS
        self._cmake.definitions[
            "ALLOW_BLAS_LAPACK_MACOS"
        ] = self.options.ALLOW_BLAS_LAPACK_MACOS
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder,
            filename="{name}-{version}.tar.xz".format(
                name=self.name, version=self.version
            ),
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindBLAS)",
            """
if(USE_SYSTEM_BLAS)
  include(ARMA_FindBLAS)
else()
  set(BLAS_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindOpenBLAS)",
            """
if(USE_SYSTEM_OPENBLAS)
  include(ARMA_FindOpenBLAS)
elseif(USE_OPENBLAS)
  find_package(OpenBLAS)
else()
  set(OpenBLAS_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindFlexiBLAS)",
            """
if(USE_SYSTEM_FLEXIBLAS)
  include(ARMA_FindFlexiBLAS)
else()
  set(FlexiBLAS_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindMKL)",
            """
if(USE_SYSTEM_MKL)
  include(ARMA_FindMKL)
else()
  set(MKL_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindLAPACK)",
            """
if(USE_SYSTEM_LAPACK)
  include(ARMA_FindLAPACK)
else()
  set(LAPACK_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindARPACK)",
            """
if(USE_SYSTEM_ARPACK)
  include(ARMA_FindARPACK)
else()
  set(ARPACK_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindSuperLU5)",
            """
if(USE_SYSTEM_SUPERLU)
  include(ARMA_FindSuperLU5)
else()
  set(SuperLU_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "include(ARMA_FindATLAS)",
            """
if(USE_SYSTEM_ATLAS)
  include(ARMA_FindATLAS)
else()
  set(ATLAS_FOUND NO)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "list(GET HDF5_INCLUDE_DIRS 0 ARMA_HDF5_INCLUDE_DIR)",
            """
if(NOT USE_SYSTEM_HDF5)
  list(GET HDF5_INCLUDE_DIRS 1 ARMA_HDF5_INCLUDE_DIR)
else()
  list(GET HDF5_INCLUDE_DIRS 0 ARMA_HDF5_INCLUDE_DIR)
endif()""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "add_library( armadillo ${PROJECT_SOURCE_DIR}/src/wrapper1.cpp ${PROJECT_SOURCE_DIR}/src/wrapper2.cpp )",
            """set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
add_library( armadillo ${PROJECT_SOURCE_DIR}/src/wrapper1.cpp ${PROJECT_SOURCE_DIR}/src/wrapper2.cpp )
            """
        )

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["armadillo"]
        self.cpp_info.names["pkg_config"] = "armadillo"

        if self.options.USE_SYSTEM_MKL:
            self.cpp_info.libs.extend(["mkl_rt"])
            self.cpp_info.libdirs.append(str(self.options.MKL_LIBRARY_PATH))

        if self.settings.build_type == "Release":
            self.cpp_info.defines.append("ARMA_NO_DEBUG")

        # The wrapper library links everything together. If disabled, system libs must be
        # linked manually
        if not self.options.ARMA_USE_WRAPPER:
            self.cpp_info.defines.append("ARMA_DONT_USE_WRAPPER")
            if self.options.ARMA_USE_ACCELERATE:
                self.cpp_info.frameworks.append("Accelerate")

        if self.options.ARMA_USE_HDF5:
            self.cpp_info.defines.append("ARMA_USE_HDF5")
            if self.options.USE_SYSTEM_HDF5 and not self.options.ARMA_USE_WRAPPER:
                self.cpp_info.system_libs.extend(
                    ["hdf5", "hdf5_cpp", "hdf5_hl", "hdf5_hl_cpp"]
                )
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_HDF5")

        if self.options.ARMA_USE_BLAS:
            self.cpp_info.defines.append("ARMA_USE_BLAS")
            if self.options.USE_SYSTEM_BLAS and not self.options.ARMA_USE_WRAPPER:
                self.cpp_info.system_libs.extend(["blas"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_BLAS")

        if self.options.ARMA_USE_LAPACK:
            self.cpp_info.defines.append("ARMA_USE_LAPACK")
            if self.options.USE_SYSTEM_LAPACK and not self.options.ARMA_USE_WRAPPER:
                self.cpp_info.system_libs.extend(["lapack"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_LAPACK")

        if self.options.ARMA_USE_ARPACK:
            self.cpp_info.defines.append("ARMA_USE_ARPACK")
            if self.options.USE_SYSTEM_ARPACK and not self.options.ARMA_USE_WRAPPER:
                self.cpp_info.system_libs.extend(["arpack"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_ARPACK")

        if self.options.ARMA_USE_SUPERLU:
            self.cpp_info.defines.append("ARMA_USE_SUPERLU")
            if self.options.USE_SYSTEM_SUPERLU and not self.options.ARMA_USE_WRAPPER:
                self.cpp_info.system_libs.extend(["superlu"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_SUPERLU")

        if self.options.ARMA_USE_ATLAS:
            self.cpp_info.defines.append("ARMA_USE_ATLAS")
            if self.options.USE_SYSTEM_ATLAS and not self.options.ARMA_USE_WRAPPER:
                self.cpp_info.system_libs.extend(["atlas"])
        else:
            self.cpp_info.defines.append("ARMA_DONT_USE_ATLAS")

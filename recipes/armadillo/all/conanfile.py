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
        "use_blas": [
            False,
            "openblas",
            "system_openblas",
            "system_blas",
            "system_mkl",
            "system_flexiblas",
            "framework_accelerate",
        ],
        "use_lapack": [
            False,
            "openblas",
            "system_openblas",
            "system_lapack",
            "system_mkl",
            "system_atlas",
            "framework_accelerate",
        ],
        "use_hdf5": [False, "hdf5", "system_hdf5"],
        "use_superlu": [False, "system_superlu"],
        "use_extern_rng": [True, False],
        "use_arpack": [False, "system_arpack"],
        "use_wrapper": [True, False],
        "mkl_library_path": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_blas": "openblas",
        "use_lapack": False,
        "use_hdf5": "hdf5",
        "use_superlu": False,
        "use_extern_rng": False,
        "use_arpack": False,
        "use_wrapper": False,
        "mkl_library_path": "",
    }
    # Values that must be set for multiple options to be valid
    _co_dependencies = {
        "system_mkl": [
            "use_blas",
            "use_lapack",
        ],
        "framework_accelerate": [
            "use_blas",
            "use_lapack",
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
            self.options.use_blas = "framework_accelerate"
            self.options.use_lapack = "framework_accelerate"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        # Use default MKL path or throw error if no default path exists
        if self.options.use_blas == "system_mkl" and not self.options.mkl_library_path:
            if self.settings.os == "Linux":
                self.options.mkl_library_path = "/opt/intel/mkl/lib/intel64"
            elif self.settings.os == "Windows":
                self.options.mkl_library_path = (
                    "C:/IntelSWTools/compilers_and_libraries/windows/mkl/lib/intel64"
                )
            else:
                raise ConanInvalidConfiguration(
                    "A default mkl_library_path value for your operating system is not available. Please specify a value for mkl_library_path"
                )

    def validate(self):
        tools.check_min_cppstd(self, "11")

        if self.settings.os != "Macos" and (
            self.options.use_blas == "framework_accelerate"
            or self.options.use_lapack == "framework_accelerate"
        ):
            raise ConanInvalidConfiguration(
                "framework_accelerate can only be used on Macos"
            )

        for value, options in self.co_dependencies.items():
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

    def requirements(self):
        # Optional requirements
        openblas = "openblas/0.3.15"
        hdf5 = "hdf5/1.12.0"
        # TODO: "atlas/3.10.3" # Pending https://github.com/conan-io/conan-center-index/issues/6757
        # TODO: "superlu/5.2.2" # Pending https://github.com/conan-io/conan-center-index/issues/6756
        # TODO: "arpack/1.0" # Pending https://github.com/conan-io/conan-center-index/issues/6755
        # TODO: "flexiblas/3.0.4" # Pending https://github.com/conan-io/conan-center-index/issues/6827

        if self.options.use_hdf5 == "hdf5":
            # Use the conan dependency if the system lib isn't being used
            self.requires(hdf5)
            self.options["hdf5"].shared = self.options.shared

        if self.options.use_blas == "openblas":
            self.requires(openblas)
            # Note that if you're relying on this to build LAPACK, you _must_ have
            # a fortran compiler installed. If you don't, OpenBLAS will build successfully but
            # without LAPACK support, which isn't obvious.
            # This can be achieved by setting the FC environment variable in your conan profile
            self.options["openblas"].build_lapack = (
                self.options.use_lapack == "openblas"
            )
            self.options["openblas"].shared = self.options.shared

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ARMA_USE_LAPACK"] = self.options.use_lapack
        self._cmake.definitions["ARMA_USE_BLAS"] = self.options.use_blas
        self._cmake.definitions["ARMA_USE_ATLAS"] = (
            self.options.use_lapack == "system_atlas"
        )
        self._cmake.definitions["ARMA_USE_HDF5"] = self.options.use_hdf5
        self._cmake.definitions["ARMA_USE_ARPACK"] = self.options.use_arpack
        self._cmake.definitions["ARMA_USE_EXTERN_RNG"] = self.options.use_extern_rng
        self._cmake.definitions["ARMA_USE_SUPERLU"] = self.options.use_superlu
        self._cmake.definitions["ARMA_USE_WRAPPER"] = self.options.use_wrapper
        self._cmake.definitions["ARMA_USE_ACCELERATE"] = (
            self.options.use_blas == "framework_accelerate"
            or self.options.use_lapack == "framework_accelerate"
        ) and self.settings.os == "Macos"
        self._cmake.definitions["DETECT_HDF5"] = self.options.use_hdf5
        self._cmake.definitions["USE_OPENBLAS"] = self.options.use_blas == "openblas"
        self._cmake.definitions["USE_SYSTEM_LAPACK"] = (
            self.options.use_lapack == "system_lapack"
        )
        self._cmake.definitions["USE_SYSTEM_BLAS"] = (
            self.options.use_blas == "system_blas"
        )
        self._cmake.definitions["USE_SYSTEM_ATLAS"] = (
            self.options.use_lapack == "system_atlas"
        )
        self._cmake.definitions["USE_SYSTEM_HDF5"] = (
            self.options.use_hdf5 == "system_hdf5"
        )
        self._cmake.definitions["USE_SYSTEM_ARPACK"] = self.options.use_arpack
        self._cmake.definitions["USE_SYSTEM_SUPERLU"] = self.options.use_superlu
        self._cmake.definitions["USE_SYSTEM_OPENBLAS"] = (
            self.options.use_blas == "system_openblas"
        )
        self._cmake.definitions["USE_SYSTEM_FLEXIBLAS"] = (
            self.options.use_blas == "system_flexiblas"
        )
        self._cmake.definitions["USE_SYSTEM_MKL"] = (
            self.options.use_blas == "system_mkl"
        )
        self._cmake.definitions["ALLOW_FLEXIBLAS_LINUX"] = (
            self.options.use_blas == "system_flexiblas" and self.settings.os == "Linux"
        )
        self._cmake.definitions["ALLOW_OPENBLAS_MACOS"] = (
            self.options.use_blas == "openblas"
            or self.options.use_blas == "system_openblas"
        ) and self.settings.os == "Macos"
        self._cmake.definitions["ALLOW_BLAS_LAPACK_MACOS"] = (
            self.options.use_blas != "framework_accelerate"
        )
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
            """,
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

        if self.options.use_blas == "system_mkl":
            self.cpp_info.libs.extend(["mkl_rt"])
            self.cpp_info.libdirs.append(str(self.options.mkl_library_path))

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
            if self.options.use_hdf5 == "system_hdf5" and not self.options.use_wrapper:
                self.cpp_info.system_libs.extend(
                    ["hdf5", "hdf5_cpp", "hdf5_hl", "hdf5_hl_cpp"]
                )
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

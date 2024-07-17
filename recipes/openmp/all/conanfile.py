from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "openmp"
    description = "Conan meta-package for OpenMP (Open Multi-Processing)"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openmp.org/"
    topics = ("parallelism", "multiprocessing")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "provider": ["auto", "native", "llvm"],
    }
    default_options = {
        "provider": "auto",
    }

    def config_options(self):
        if self.settings.compiler == "clang" and self.settings.os == "Linux":
            # The Clang toolchain on Linux distros typically ships without libomp.
            # FreeBSD includes it, though.
            self.options.provider = "llvm"
        elif self.settings.compiler == "apple-clang":
            self.options.provider = "llvm"
        else:
            self.options.provider = "native"

    def requirements(self):
        if self.options.provider == "llvm":
            # Note: MSVC ships with an optional LLVM OpenMP implementation, but it would require reliably setting
            # `OpenMP_RUNTIME_MSVC=llvm` in CMake for all consumers of this recipe, which is not possible in a meta-package.
            # TODO: match the major version of llvm-openmp to the version of Clang / LLVM.
            self.requires("llvm-openmp/18.1.8", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.options.provider == "native" and self._openmp_flags is None:
            raise ConanInvalidConfiguration(
                f"{self.settings.compiler} is not supported by this recipe. Contributions are welcome!"
            )

        if self.options.provider == "llvm":
            if self.settings.compiler not in ["clang", "apple-clang"] and not is_msvc(self):
                # More info: https://cpufun.substack.com/p/is-mixing-openmp-runtimes-safe
                self.output.warning(
                    "Warning: Using a non-native OpenMP implementation can be bug-prone. "
                    "Make sure you avoid accidental linking against the native implementation through external libraries."
                )

    @property
    def _openmp_flags(self):
        # Based on https://github.com/Kitware/CMake/blob/v3.30.0/Modules/FindOpenMP.cmake#L119-L154
        if self.settings.compiler == "gcc":
            return ["-fopenmp"]
        elif self.settings.compiler == "clang":
            return ["-fopenmp=libomp"]
        elif self.settings.compiler == "apple-clang":
            return ["-Xclang", "-fopenmp"]
        elif is_msvc(self):
            # Use `-o provider=llvm` for `-openmp=llvm` in MSVC.
            # TODO: add support for `-openmp=experimental`?
            return ["-openmp"]
        elif self.settings.compiler == "intel-cc":
            if self.settings.os == "Windows":
                return ["-Qopenmp"]
            else:
                return ["-qopenmp"]
        elif self.settings.compiler == "sun-cc":
            return ["-xopenmp"]

        # The following compilers are not currently covered by settings.yml,
        # but are included for completeness.
        elif self.settings.compiler == "hp":
            return ["+Oopenmp"]
        elif self.settings.compiler == "intel-llvm":
            if self.settings.get_safe("compiler.frontend") == "msvc":
                return ["-Qiopenmp"]
            else:
                return ["-fiopenmp"]
        elif self.settings.compiler == "pathscale":
            return ["-openmp"]
        elif self.settings.compiler == "nag":
            return ["-openmp"]
        elif self.settings.compiler == "absoft":
            return ["-openmp"]
        elif self.settings.compiler == "nvhpc":
            return ["-mp"]
        elif self.settings.compiler == "pgi":
            return ["-mp"]
        elif self.settings.compiler == "xl":
            return ["-qsmp=omp"]
        elif self.settings.compiler == "cray":
            return ["-h", "omp"]
        elif self.settings.compiler == "fujitsu":
            return ["-Kopenmp"]
        elif self.settings.compiler == "fujitsu-clang":
            return ["-fopenmp"]

        return None

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")

        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        if self.options.provider == "native":
            # Rely on CMake's FindOpenMP.cmake and an OpenMP implementation provided by the compiler.
            # Export appropriate flags for the transitive use case.
            openmp_flags = self._openmp_flags
            self.cpp_info.sharedlinkflags = openmp_flags
            self.cpp_info.exelinkflags = openmp_flags
            self.cpp_info.cflags = openmp_flags
            self.cpp_info.cxxflags = openmp_flags

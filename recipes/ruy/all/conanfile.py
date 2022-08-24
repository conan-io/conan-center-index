import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class RuyConan(ConanFile):
    name = "ruy"
    description = "ruy is a matrix multiplication library.\n" \
                  "Its focus is to cover the matrix multiplication needs of neural network inference engines\n"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/ruy"
    license = "Apache-2.0"
    topics = ("matrix", "multiplication", "neural", "network", "AI", "tensorflow")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("Compiler is unknown. Assuming it supports C++14.")
        elif tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Build requires support for C++14. Minimum version for {} is {}"
                .format(str(self.settings.compiler), minimum_version))

        if str(self.settings.compiler) == "clang" and tools.scm.Version(self, self.settings.compiler.version) <= 5 and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration("Debug builds are not supported on older versions of Clang (<=5)")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("cpuinfo/cci.20201217")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["RUY_MINIMAL_BUILD"] = True
        self._cmake.configure()
        return self._cmake


    def build(self):
        # 1. Allow Shared builds
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "ruy_cc_library.cmake"),
                              "add_library(${_NAME} STATIC",
                              "add_library(${_NAME}"
                              )

        # 2. Shared builds fail with undefined symbols without this fix.
        # This is because ruy only links to 'cpuinfo' but it also needs 'clog' (from the same package)
        cpuinfoLibs = self.deps_cpp_info["cpuinfo"].libs + self.deps_cpp_info["cpuinfo"].system_libs
        libsListAsString = ";".join(cpuinfoLibs)
        if int(self.version.strip('cci.')) < 20220628:
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "ruy", "CMakeLists.txt"),
                                  "set(ruy_6_cpuinfo \"cpuinfo\")",
                                  f"set(ruy_6_cpuinfo \"{libsListAsString}\")"
                                  )
        else:
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "ruy", "CMakeLists.txt"),
                                  "set(ruy_6_cpuinfo_cpuinfo \"cpuinfo::cpuinfo\")",
                                  f"set(ruy_6_cpuinfo_cpuinfo \"{libsListAsString}\")"
                                  )

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst=os.path.join("include", "ruy"), src=os.path.join(self._source_subfolder, "ruy"))
        self.copy(pattern="*", dst="lib", src="lib")
        self.copy(pattern="*", dst="bin", src="bin")

        tools.files.rm(self, self.package_folder, "*.pdb")

    def package_info(self):
        self.cpp_info.libs = ["ruy_frontend",
                            "ruy_context",
                            "ruy_trmul",
                            "ruy_thread_pool",
                            "ruy_blocking_counter",
                            "ruy_prepare_packed_matrices",
                            "ruy_ctx",
                            "ruy_allocator",
                            "ruy_prepacked_cache",
                            "ruy_tune",
                            "ruy_wait",
                            "ruy_apply_multiplier",
                            "ruy_block_map",
                            "ruy_context_get_ctx",
                            "ruy_cpuinfo",
                            "ruy_denormal",
                            "ruy_have_built_path_for_avx",
                            "ruy_have_built_path_for_avx2_fma",
                            "ruy_have_built_path_for_avx512",
                            "ruy_kernel_arm",
                            "ruy_kernel_avx",
                            "ruy_kernel_avx2_fma",
                            "ruy_kernel_avx512",
                            "ruy_pack_arm",
                            "ruy_pack_avx",
                            "ruy_pack_avx2_fma",
                            "ruy_pack_avx512",
                            "ruy_system_aligned_alloc",
                            "ruy_profiler_instrumentation",
                            "ruy_profiler_profiler"
                            ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])

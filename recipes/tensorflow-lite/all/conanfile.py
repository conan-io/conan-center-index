from conans import ConanFile, CMake, tools
from conan.tools import files
from conan.tools.scm import Version
from conans.errors import ConanInvalidConfiguration
import functools
import os
import textwrap

required_conan_version = ">=1.43.0"


class TensorflowLiteConan(ConanFile):
    name = "tensorflow-lite"
    license = "Apache-2.0"
    homepage = "https://www.tensorflow.org/lite/guide"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("TensorFlow Lite is a set of tools that enables on-device machine learning "
                   "by helping developers run their models on mobile, embedded, and IoT devices.")
    topics = ("machine-learning", "neural-networks", "deep-learning")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ruy": [True, False],
        "with_nnapi": [True, False],
        "with_mmap": [True, False],
        "with_xnnpack": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ruy": False,
        "with_nnapi": False,
        "with_mmap": True,
        "with_xnnpack": True
    }


    short_paths = True
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "src"

    @property
    def _build_subfolder(self):
        return "build"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])
        if Version(self.version) >= "2.9.1":
            self.copy("patches/remove_simple_memory_arena_debug_dump.patch")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_nnapi
            del self.options.with_mmap
        if self.settings.os == "Macos":
            del self.options.with_nnapi

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("abseil/20211102.0")
        self.requires("eigen/3.4.0")
        self.requires("farmhash/cci.20190513")
        self.requires("fft/cci.20061228")
        self.requires("flatbuffers/2.0.5")
        self.requires("gemmlowp/cci.20210928")
        if self.settings.arch in ("x86", "x86_64"):
            self.requires("intel-neon2sse/cci.20210225")
        self.requires("ruy/cci.20220628")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20220621")

        if self.options.with_xnnpack or self.options.get_safe("with_nnapi", False):
            self.requires("fp16/cci.20210320")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(f"{self.name} requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++14, which your compiler does not support.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
        files.apply_conandata_patches(self)

        # Shared build fails on Windows with
        # simple_memory_arena_debug_dump.obj : error LNK2005: "void __cdecl tflite::DumpArenaInfo(...) already defined in simple_memory_arena.obj
        # Resolve the conflict by removing the conflicting
        # implementation for now.
        if Version(self.version) >= "2.9.1" and self.settings.os == "Windows" and self.options.shared:
            tools.patch(patch_file="patches/remove_simple_memory_arena_debug_dump.patch", base_path="src")

        # All CMake targets will be provided by Conan through the wrapper, removing every occurrence of `find_package`
        cmake_lists_path = os.path.join(self.source_folder, self._source_subfolder, "tensorflow/lite/CMakeLists.txt")
        original_content = open(cmake_lists_path, "r").readlines()
        patched_content = "".join(line for line in original_content if "find_package" not in line)
        open(cmake_lists_path, "w").write(patched_content)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions.update({
            "CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS": True,
            "TFLITE_ENABLE_RUY": self.options.with_ruy,
            "TFLITE_ENABLE_NNAPI": self.options.get_safe("with_nnapi", False),
            "TFLITE_ENABLE_GPU": False,
            "TFLITE_ENABLE_XNNPACK": self.options.with_xnnpack,
            "TFLITE_ENABLE_MMAP": self.options.get_safe("with_mmap", False)
        })
        if self.settings.arch == "armv8":
            # Not defined by Conan for Apple Silicon. See https://github.com/conan-io/conan/pull/8026
            cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "arm64"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    @staticmethod
    def _create_cmake_module_alias_target(module_file):
        aliased = "tensorflowlite::tensorflowlite"
        alias = "tensorflow::tensorflowlite"
        content = textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        tools.save(module_file, content)

    @property
    def _module_file(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", "tensorflow", "lite"), src=os.path.join(self._source_subfolder, "tensorflow", "lite"))
        self.copy("*", dst="lib", src=os.path.join(self._build_subfolder, "lib"))
        if self.options.shared:
            self.copy("*", dst="bin", src=os.path.join(self._build_subfolder, "bin"))
            tools.remove_files_by_mask(self.package_folder, "*.pdb")
        self._create_cmake_module_alias_target(os.path.join(self.package_folder, self._module_file))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tensorflowlite")
        self.cpp_info.set_property("cmake_target_name", "tensorflow::tensorflowlite")

        self.cpp_info.names["cmake_find_package"] = "tensorflowlite"
        self.cpp_info.names["cmake_find_package_multi"] = "tensorflowlite"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file]

        defines = []
        if not self.options.shared:
            defines.append("TFL_STATIC_LIBRARY_BUILD")
        if self.options.with_ruy:
            defines.append("TFLITE_WITH_RUY")

        self.cpp_info.defines = defines
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

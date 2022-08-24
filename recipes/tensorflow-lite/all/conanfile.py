from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
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
        "with_xnnpack": True,
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
            if self.settings.os == "Linux":
                self.options["ruy"].shared = True

    def requirements(self):
        self.requires("abseil/20211102.0")
        self.requires("eigen/3.4.0")
        self.requires("farmhash/cci.20190513")
        self.requires("fft/cci.20061228")
        self.requires("flatbuffers/2.0.5")
        self.requires("gemmlowp/cci.20210928")
        if self.settings.arch in ("x86", "x86_64"):
            self.requires("intel-neon2sse/cci.20210225")
        self.requires("ruy/cci.20210622")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20211210")
            self.requires("fp16/cci.20210320")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(f"{self.name} requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(f"{self.name} requires C++14, which your compiler does not support.")
        if self.options.shared:
            if self.settings.os == "Linux" and not self.options["ruy"].shared:
                raise ConanInvalidConfiguration(
                        f"The project {self.name}/{self.version} with shared=True on Linux requires ruy:shared=True")

    def build_requirements(self):
        self.build_requires("ninja/1.10.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions.update({
            "CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS": True,
            "TFLITE_ENABLE_RUY": self.options.get_safe("with_ruy", False),
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
            tools.files.rm(self, self.package_folder, "*.pdb")
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
        if self.options.get_safe("with_ruy", False):
            defines.append("TFLITE_WITH_RUY")

        self.cpp_info.defines = defines
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

import os
import textwrap

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.36.0"


class TensorflowLiteConan(ConanFile):
    name = "tensorflow-lite"
    license = "Apache-2.0"
    homepage = "https://www.tensorflow.org/lite/guide"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("TensorFlow Lite is a set of tools that enables on-device machine learning "
                   "by helping developers run their models on mobile, embedded, and IoT devices.")
    topics = ("machine-learning", "neural-networks", "deep-learning")
    settings = "os", "compiler", "build_type", "arch"
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
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/**"]

    _cmake = None

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build_requirements(self):
        self.build_requires("ninja/1.10.2")

    def requirements(self):
        self.requires("abseil/20210324.2")
        self.requires("eigen/3.4.0")
        self.requires("farmhash/cci.20190513")
        self.requires("fft/cci.20061228")
        self.requires("flatbuffers/2.0.0")
        self.requires("gemmlowp/cci.20210928")
        if self.settings.arch in ("x86", "x86_64"):
            self.requires("intel-neon2sse/cci.20210225")
        self.requires("ruy/cci.20210622")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20211026")
            self.requires("fp16/cci.20200514")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions.update({
            "CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS": True,
            "TFLITE_ENABLE_RUY": self.options.get_safe("with_ruy", False),
            "TFLITE_ENABLE_NNAPI": self.options.get_safe("with_nnapi", False),
            "TFLITE_ENABLE_GPU": False,
            "TFLITE_ENABLE_XNNPACK": self.options.with_xnnpack,
            "TFLITE_ENABLE_MMAP": self.options.get_safe("with_mmap", False)
        })
        if self.settings.arch == "armv8":
            # Not defined by Conan for Apple Silicon. See https://github.com/conan-io/conan/pull/8026
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "arm64"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

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

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", "tensorflow", "lite"), src=os.path.join(self._source_subfolder, "tensorflow", "lite"))
        self.copy("*", dst="lib", src=os.path.join(self._build_subfolder, "lib"))
        if self.options.shared:
            self.copy("*", dst="bin", src=os.path.join(self._build_subfolder, "bin"))
            tools.remove_files_by_mask(self.package_folder, "*.pdb")
        self._create_cmake_module_alias_target(os.path.join(self.package_folder, self._module_subfolder, self._module_file))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tensorflowlite")
        self.cpp_info.set_property("cmake_target_name", "tensorflowlite")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join(self._module_subfolder, self._module_file)])
        defines = []
        if not self.options.shared:
            defines.append("TFL_STATIC_LIBRARY_BUILD")
        if self.options.get_safe("with_ruy", False):
            defines.append("TFLITE_WITH_RUY")

        self.cpp_info.defines = defines
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")

from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.36.0"


class ShadercConan(ConanFile):
    name = "shaderc"
    description = "A collection of tools, libraries and tests for shader compilation."
    license = "Apache-2.0"
    topics = ("glsl", "hlsl", "msl", "spirv", "spir-v", "glslc", "spvc")
    homepage = "https://github.com/google/shaderc"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "spvc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "spvc": False,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) >= "2020.4":
            del self.options.spvc

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _get_compatible_spirv_tools_version(self):
        return {
            "2021.1": "2021.2",
            "2019.0": "2020.5"
        }.get(str(self.version), False)

    @property
    def _get_compatible_glslang_version(self):
        return {
            "2021.1": "11.5.0",
            "2019.0": "8.13.3559"
        }.get(str(self.version), False)

    def requirements(self):
        self.requires("glslang/{}".format(self._get_compatible_glslang_version))
        self.requires("spirv-tools/{}".format(self._get_compatible_spirv_tools_version))
        if self.options.get_safe("spvc", False):
           self.requires("spirv-cross/20210115")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["SHADERC_ENABLE_SPVC"] = self.options.get_safe("spvc", False)
        self._cmake.definitions["SHADERC_SKIP_INSTALL"] = False
        self._cmake.definitions["SHADERC_SKIP_TESTS"] = True
        self._cmake.definitions["SHADERC_SPVC_ENABLE_DIRECT_LOGGING"] = False
        self._cmake.definitions["SHADERC_SPVC_DISABLE_CONTEXT_LOGGING"] = False
        self._cmake.definitions["SHADERC_ENABLE_WERROR_COMPILE"] = False
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["SHADERC_ENABLE_SHARED_CRT"] = str(self.settings.compiler.runtime).startswith("MD")
        self._cmake.definitions["ENABLE_CODE_COVERAGE"] = False
        if tools.is_apple_os(self.settings.os):
            self._cmake.definitions["CMAKE_MACOSX_BUNDLE"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "shaderc" if self.options.shared else "shaderc_static")
        self.cpp_info.libs = self._get_ordered_libs()
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))
        if self.options.shared:
            self.cpp_info.defines.append("SHADERC_SHAREDLIB")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

    def _get_ordered_libs(self):
        libs = ["shaderc_shared" if self.options.shared else "shaderc"]
        if not self.options.shared:
            libs.append("shaderc_util")
        if self.options.get_safe("spvc", False):
            libs.append("shaderc_spvc_shared" if self.options.shared else "shaderc_spvc")
        return libs

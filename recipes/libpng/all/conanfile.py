from conans import ConanFile, CMake, tools
import glob
import os

required_conan_version = ">=1.33.0"


class LibpngConan(ConanFile):
    name = "libpng"
    description = "libpng is the official PNG file format reference library."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.libpng.org"
    license = "libpng-2.0"
    topics = ("conan", "png", "libpng")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "neon": [True, "check", False],
        "msa": [True, False],
        "sse": [True, False],
        "vsx": [True, False],
        "api_prefix": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "neon": True,
        "msa": True,
        "sse": True,
        "vsx": True,
        "api_prefix": "",
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = ["cmake", "cmake_find_package"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_neon_support(self):
        return "arm" in self.settings.arch

    @property
    def _has_msa_support(self):
        return "mips" in self.settings.arch

    @property
    def _has_sse_support(self):
        return self.settings.arch in ["x86", "x86_64"]

    @property
    def _has_vsx_support(self):
        return "ppc" in self.settings.arch

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_neon_support:
            del self.options.neon
        if not self._has_msa_support:
            del self.options.msa
        if not self._has_sse_support:
            del self.options.sse
        if not self._has_vsx_support:
            del self.options.vsx

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "find_library(M_LIBRARY m)",
                              "set(M_LIBRARY m)")

        if tools.os_info.is_windows:
            if self.settings.compiler == "Visual Studio":
                tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                     'OUTPUT_NAME "${PNG_LIB_NAME}_static',
                                     'OUTPUT_NAME "${PNG_LIB_NAME}')
            else:
                tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                      'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}',
                                      'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/$<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}')

    @property
    def _neon_msa_sse_vsx_mapping(self):
        return {
            "True": "on",
            "False": "off",
            "check": "check",
        }

    @property
    def _libpng_cmake_system_processor(self):
        # FIXME: too specific and error prone, should be delegated to a conan helper function
        # It should satisfy libpng CMakeLists specifically, do not use it naively in an other recipe
        if "mips" in self.settings.arch:
            return "mipsel"
        if "ppc" in self.settings.arch:
            return "powerpc"
        return str(self.settings.arch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PNG_TESTS"] = False
        self._cmake.definitions["PNG_SHARED"] = self.options.shared
        self._cmake.definitions["PNG_STATIC"] = not self.options.shared
        self._cmake.definitions["PNG_DEBUG"] = self.settings.build_type == "Debug"
        self._cmake.definitions["PNG_PREFIX"] = self.options.api_prefix
        if tools.cross_building(self.settings):
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = self._libpng_cmake_system_processor
        if self._has_neon_support:
            self._cmake.definitions["PNG_ARM_NEON"] = self._neon_msa_sse_vsx_mapping[str(self.options.neon)]
        if self._has_msa_support:
            self._cmake.definitions["PNG_MIPS_MSA"] = self._neon_msa_sse_vsx_mapping[str(self.options.msa)]
        if self._has_sse_support:
            self._cmake.definitions["PNG_INTEL_SSE"] = self._neon_msa_sse_vsx_mapping[str(self.options.sse)]
        if self._has_vsx_support:
            self._cmake.definitions["PNG_POWERPC_VSX"] = self._neon_msa_sse_vsx_mapping[str(self.options.vsx)]
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        if self.options.shared:
            for binfile in glob.glob(os.path.join(self.package_folder, "bin", "*")):
                if not binfile.endswith(".dll"):
                    os.remove(binfile)
        else:
            tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "libpng"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PNG"
        self.cpp_info.names["cmake_find_package_multi"] = "PNG"
        self.cpp_info.names["pkg_config"] = "libpng" # TODO: we should also create libpng16.pc file

        prefix = "lib" if self.settings.compiler == "Visual Studio" else ""
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["{}png16{}".format(prefix, suffix)]
        if self.settings.os in ["Linux", "Android", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

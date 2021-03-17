from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os
import textwrap

required_conan_version = ">=1.33.0"


class FbgemmConan(ConanFile):
    name = "fbgemm"
    description = "FBGEMM (Facebook GEneral Matrix Multiplication) is a " \
                  "low-precision, high-performance matrix-matrix multiplications " \
                  "and convolution library for server-side inference."
    license = "BSD-3-Clause"
    topics = ("conan", "fbgemm", "matrix", "convolution")
    homepage = "https://github.com/pytorch/FBGEMM"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

    def requirements(self):
        self.requires("asmjit/cci.20210306")
        self.requires("cpuinfo/cci.20201217")

    def validate(self):
        compiler = self.settings.compiler
        compiler_version = tools.Version(self.settings.compiler.version)
        if (compiler == "Visual Studio" and compiler_version < "15") or \
           (compiler == "gcc" and compiler_version < "5"):
            raise ConanInvalidConfiguration("fbgemm doesn't support {} {}".format(str(compiler), compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("FBGEMM-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # Don't inject definitions from upstream dependencies
        tools.replace_in_file(cmakelists, "target_compile_definitions(fbgemm_generic PRIVATE ASMJIT_STATIC)", "")
        tools.replace_in_file(cmakelists, "target_compile_definitions(fbgemm_avx2 PRIVATE ASMJIT_STATIC)", "")
        tools.replace_in_file(cmakelists, "target_compile_definitions(fbgemm_avx512 PRIVATE ASMJIT_STATIC)", "")
        # Honor runtime from profile
        tools.replace_in_file(cmakelists, "if(${flag_var} MATCHES \"/MD\")", "if(0)")
        # Do not install stuff related to dependencies
        tools.replace_in_file(cmakelists, "if(MSVC)\n  if(FBGEMM_LIBRARY_TYPE STREQUAL \"shared\")", "if(0)\nif(0)")
        # Properly link to obj targets
        tools.replace_in_file(cmakelists,
                              "add_dependencies(fbgemm asmjit cpuinfo)",
                              "target_link_libraries(fbgemm_generic asmjit cpuinfo)\n"
                              "target_link_libraries(fbgemm_avx2 asmjit cpuinfo)\n"
                              "target_link_libraries(fbgemm_avx512 asmjit cpuinfo)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FBGEMM_LIBRARY_TYPE"] = "shared" if self.options.shared else "static"
        self._cmake.definitions["FBGEMM_BUILD_TESTS"] = False
        self._cmake.definitions["FBGEMM_BUILD_BENCHMARKS"] = False
        self._cmake.definitions["FBGEMM_BUILD_DOCS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"fbgemm": "fbgemm::fbgemm"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "fbgemmLibrary"
        self.cpp_info.filenames["cmake_find_package_multi"] = "fbgemmLibrary"
        self.cpp_info.names["cmake_find_package"] = "fbgemm"
        self.cpp_info.names["cmake_find_package_multi"] = "fbgemm"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.libs = ["fbgemm"]
        if not self.options.shared:
            self.cpp_info.defines = ["FBGEMM_STATIC"]

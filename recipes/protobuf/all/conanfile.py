import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class ProtobufConan(ConanFile):
    name = "protobuf"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("conan", "protobuf", "protocol-buffers",
              "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    short_paths = True
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "with_zlib": [True, False], "fPIC": [True, False], "lite": [True, False]}
    default_options = {"with_zlib": False, "shared": False, "fPIC": True, "lite": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

            if self.settings.os == "Windows" and self.settings.compiler in ["Visual Studio", "clang"] and "MT" in self.settings.compiler.runtime:
                raise ConanInvalidConfiguration("Protobuf can't be built with shared + MT(d) runtimes")

            if tools.is_apple_os(self.settings.os):
                raise ConanInvalidConfiguration("Protobuf could not be built as shared library for Mac.")

        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version) < "14":
                raise ConanInvalidConfiguration("On Windows Protobuf can only be built with "
                                                "Visual Studio 2015 or higher.")
    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake", "protobuf")

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CMAKE_INSTALL_CMAKEDIR"] = self._cmake_install_base_path.replace("\\", "/")
            self._cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
            self._cmake.definitions["protobuf_BUILD_TESTS"] = False
            self._cmake.definitions["protobuf_BUILD_PROTOC_BINARIES"] = True
            self._cmake.definitions["protobuf_BUILD_LIBPROTOC"] = True
            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in str(self.settings.compiler.runtime)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
            "@_protobuf_FIND_ZLIB@",
            "# CONAN PATCH _protobuf_FIND_ZLIB@"
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
            "include(\"${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake\")",
            "# CONAN PATCH include(\"${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake\")"
        )
        if tools.Version(self.version) < "3.12.0":
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
                """COMMAND  protobuf::protoc
      ARGS --${protobuf_generate_LANGUAGE}_out ${_dll_export_decl}${protobuf_generate_PROTOC_OUT_DIR} ${_protobuf_include_path} ${_abs_file}
      DEPENDS ${_abs_file} protobuf::protoc""",
                """COMMAND "${CMAKE_COMMAND}"  #FIXME: use conan binary component
      ARGS -E env "DYLD_LIBRARY_PATH=${Protobuf_LIB_DIRS}:${CONAN_LIB_DIRS}:${Protobuf_LIB_DIRS_RELEASE}:${Protobuf_LIB_DIRS_DEBUG}:${Protobuf_LIB_DIRS_RELWITHDEBINFO}:${Protobuf_LIB_DIRS_MINSIZEREL}" protoc --${protobuf_generate_LANGUAGE}_out ${_dll_export_decl}${protobuf_generate_PROTOC_OUT_DIR} ${_protobuf_include_path} ${_abs_file}
      DEPENDS ${_abs_file} USES_TERMINAL"""
            )
        else:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
                """COMMAND  protobuf::protoc
      ARGS --${protobuf_generate_LANGUAGE}_out ${_dll_export_decl}${protobuf_generate_PROTOC_OUT_DIR} ${_plugin} ${_protobuf_include_path} ${_abs_file}
      DEPENDS ${_abs_file} protobuf::protoc""",
                """COMMAND "${CMAKE_COMMAND}"  #FIXME: use conan binary component
      ARGS -E env "DYLD_LIBRARY_PATH=${Protobuf_LIB_DIRS}:${CONAN_LIB_DIRS}:${Protobuf_LIB_DIRS_RELEASE}:${Protobuf_LIB_DIRS_DEBUG}:${Protobuf_LIB_DIRS_RELWITHDEBINFO}:${Protobuf_LIB_DIRS_MINSIZEREL}" protoc --${protobuf_generate_LANGUAGE}_out ${_dll_export_decl}${protobuf_generate_PROTOC_OUT_DIR} ${_plugin} ${_protobuf_include_path} ${_abs_file}
      DEPENDS ${_abs_file} USES_TERMINAL"""
            )

        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-module.cmake.in"),
            'if(DEFINED Protobuf_SRC_ROOT_FOLDER)',
            """if(0)
if(DEFINED Protobuf_SRC_ROOT_FOLDER)""",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-module.cmake.in"),
            '# Define upper case versions of output variables',
            'endif()',
        )

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config-version.cmake"))
        os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-targets.cmake"))
        os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-targets-{}.cmake".format(str(self.settings.build_type).lower())))
        os.rename(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config.cmake"),
                  os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-generate.cmake"))

        if not self.options.lite:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "libprotobuf-lite.*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "libprotobuf-lite.*")

    def package_info(self):
        # The module name is Protobuf while the config name is protobuf
        self.cpp_info.filenames["cmake_find_package"] = "Protobuf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "protobuf"

        self.cpp_info.names["cmake_find_package"] = "protobuf"
        self.cpp_info.names["cmake_find_package_multi"] = "protobuf"

        lib_prefix = "lib" if self.settings.compiler == "Visual Studio" else ""
        lib_suffix = "d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.components["libprotobuf"].names["cmake_find_package"] = "libprotobuf"
        self.cpp_info.components["libprotobuf"].names["cmake_find_package_multi"] = "libprotobuf"
        self.cpp_info.components["libprotobuf"].names["pkg_config"] = "protobuf"
        self.cpp_info.components["libprotobuf"].libs = [lib_prefix + "protobuf" + lib_suffix]
        if self.options.with_zlib:
            self.cpp_info.components["libprotobuf"].requires = ["zlib::zlib"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libprotobuf"].system_libs.append("pthread")
            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.components["libprotobuf"].system_libs.append("atomic")
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.components["libprotobuf"].defines = ["PROTOBUF_USE_DLLS"]

        self.cpp_info.components["libprotobuf"].builddirs = [
            self._cmake_install_base_path,
        ]

        self.cpp_info.components["libprotobuf"].builddirs = [self._cmake_install_base_path]
        self.cpp_info.components["libprotobuf"].build_modules.extend([
            os.path.join(self._cmake_install_base_path, "protobuf-generate.cmake"),
            os.path.join(self._cmake_install_base_path, "protobuf-module.cmake"),
            os.path.join(self._cmake_install_base_path, "protobuf-options.cmake"),
        ])

        self.cpp_info.components["libprotoc"].name = "libprotoc"
        self.cpp_info.components["libprotoc"].libs = [lib_prefix + "protoc" + lib_suffix]
        self.cpp_info.components["libprotoc"].requires = ["libprotobuf"]

        self.cpp_info.components["protoc"].name = "protoc"
        self.cpp_info.components["protoc"].requires.extend(["libprotoc", "libprotobuf"])

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        if self.options.lite:
            self.cpp_info.components["libprotobuf-lite"].names["cmake_find_package"] = "libprotobuf-lite"
            self.cpp_info.components["libprotobuf-lite"].names["cmake_find_package_multi"] = "libprotobuf-lite"
            self.cpp_info.components["libprotobuf-lite"].names["pkg_config"] = "protobuf-lite"
            self.cpp_info.components["libprotobuf-lite"].libs = [lib_prefix + "protobuf-lite" + lib_suffix]
            if self.settings.os == "Linux":
                self.cpp_info.components["libprotobuf-lite"].system_libs.append("pthread")
                if self._is_clang_x86 or "arm" in str(self.settings.arch):
                    self.cpp_info.components["libprotobuf-lite"].system_libs.append("atomic")
            if self.settings.os == "Windows":
                if self.options.shared:
                    self.cpp_info.components["libprotobuf-lite"].defines = ["PROTOBUF_USE_DLLS"]

            self.cpp_info.components["libprotobuf-lite"].builddirs = [self._cmake_install_base_path]
            self.cpp_info.components["libprotobuf-lite"].build_modules.extend([
                os.path.join(self._cmake_install_base_path, "protobuf-generate.cmake"),
                os.path.join(self._cmake_install_base_path, "protobuf-module.cmake"),
                os.path.join(self._cmake_install_base_path, "protobuf-options.cmake"),
            ])

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

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = Version(self.settings.compiler.version.value)
            if compiler_version < "14":
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
            self._cmake.definitions["protobuf_BUILD_TESTS"] = False
            self._cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
            "@_protobuf_FIND_ZLIB@",
            "# CONAN PATCH @_protobuf_FIND_ZLIB@"
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
            'include("${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake")',
            '# CONAN PATCH include("${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake")'
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
            'COMMAND  protobuf::protoc',
            'COMMAND "${CMAKE_COMMAND}"',
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in"),
            'ARGS --${protobuf_generate_LANGUAGE}_out',
            'ARGS -E env "DYLD_LIBRARY_PATH=${Protobuf_LIB_DIRS}:${CONAN_LIB_DIRS}:${Protobuf_LIB_DIRS_RELEASE}:${Protobuf_LIB_DIRS_DEBUG}:${Protobuf_LIB_DIRS_RELWITHDEBINFO}:${Protobuf_LIB_DIRS_MINSIZEREL}" protoc --${protobuf_generate_LANGUAGE}_out',
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-module.cmake.in"),
            '# Environment',
            'if(0)',
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "protobuf-module.cmake.in"),
            '# Version info variable',
            'endif()',
        )
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.unlink(os.path.join(self.package_folder, "lib", "cmake", "protobuf", "protobuf-config-version.cmake"))
        os.unlink(os.path.join(self.package_folder, "lib", "cmake", "protobuf", "protobuf-targets.cmake"))
        os.unlink(os.path.join(self.package_folder, "lib", "cmake", "protobuf", "protobuf-targets-{}.cmake".format(str(self.settings.build_type).lower())))
        os.rename(os.path.join(self.package_folder, "lib", "cmake", "protobuf", "protobuf-config.cmake"),
                  os.path.join(self.package_folder, "lib", "cmake", "protobuf", "protobuf-generate.cmake"))

        if self.options.lite:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "libprotobuf.*")):
                os.remove(f)
        else:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "libprotobuf-lite.*")):
                os.remove(f)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Protobuf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Protobuf"

        self.cpp_info.names["cmake_find_package"] = "protobuf"
        self.cpp_info.names["cmake_find_package_multi"] = "protobuf"

        self.cpp_info.components["protoc"].name = "protoc"
        if self.options.with_zlib:
            self.cpp_info.components["protoc"].requires.append("zlib::zlib")

        self.cpp_info.components["libprotoc"].name = "libprotoc"
        self.cpp_info.components["libprotoc"].libs = ["protoc"]
        self.cpp_info.components["libprotoc"].requires = ["libprotobuf"]

        if not self.options.lite:
            self.cpp_info.components["libprotobuf"].name = "libprotobuf"
            self.cpp_info.components["libprotobuf"].libs = ["protobuf"]
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

            self.cpp_info.components["libprotobuf"].build_modules.extend([
                os.path.join(self._cmake_install_base_path, "protobuf-generate.cmake"),
                os.path.join(self._cmake_install_base_path, "protobuf-module.cmake"),
                os.path.join(self._cmake_install_base_path, "protobuf-options.cmake"),
            ])

        else:
            self.cpp_info.components["libprotobuf-lite"].name = "libprotobuf-lite"
            self.cpp_info.components["libprotobuf-lite"].libs = ["protobuf-lite"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libprotobuf-lite"].system_libs.append("pthread")
                if self._is_clang_x86 or "arm" in str(self.settings.arch):
                    self.cpp_info.components["libprotobuf-lite"].system_libs.append("atomic")
            if self.settings.os == "Windows":
                if self.options.shared:
                    self.cpp_info.components["libprotobuf-lite"].defines = ["PROTOBUF_USE_DLLS"]


        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

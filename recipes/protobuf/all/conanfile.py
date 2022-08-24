from conan.tools.files import rename, get, apply_conandata_patches, replace_in_file, rmdir, rm
from conan.tools.microsoft import msvc_runtime_flag
from conan.tools.scm import Version
from conan.tools.build import cross_building
from conan.errors import ConanInvalidConfiguration
from conan import ConanFile
from conans import CMake
# TODO: Update to conan.tools.apple after 1.51.3
from conan.tools.apple import is_apple_os

import functools
import os
import textwrap

required_conan_version = ">=1.43.0"


class ProtobufConan(ConanFile):
    name = "protobuf"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_rtti": [True, False],
        "lite": [True, False],
        "debug_suffix": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_rtti": True,
        "lite": False,
        "debug_suffix": True,
    }

    short_paths = True
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_clang_cl(self):
        return self.settings.compiler == 'clang' and self.settings.os == 'Windows'

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    @property
    def _can_disable_rtti(self):
        return Version(self.version) >= "3.15.4"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._can_disable_rtti:
            del self.options.with_rtti

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.options.shared and str(self.settings.compiler.get_safe("runtime")) in ["MT", "MTd", "static"]:
            raise ConanInvalidConfiguration("Protobuf can't be built with shared + MT(d) runtimes")

        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version) < "14":
                raise ConanInvalidConfiguration("On Windows Protobuf can only be built with "
                                                "Visual Studio 2015 or higher.")

        if self.settings.compiler == "clang":
            if Version(self.version) >= "3.15.4" and Version(self.settings.compiler.version) < "4":
                raise ConanInvalidConfiguration("protobuf {} doesn't support clang < 4".format(self.version))

        if hasattr(self, "settings_build") and cross_building(self) and \
           self.settings.os == "Macos" and self.options.shared:
            # FIXME: should be allowed, actually build succeeds but it fails at build time of test package due to SIP
            raise ConanInvalidConfiguration("protobuf shared not supported yet in CCI while cross-building on Macos")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake", "protobuf")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_CMAKEDIR"] = self._cmake_install_base_path.replace("\\", "/")
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_BUILD_PROTOC_BINARIES"] = True
        if not self.options.debug_suffix:
            cmake.definitions["protobuf_DEBUG_POSTFIX"] = ""
        if Version(self.version) >= "3.14.0":
            cmake.definitions["protobuf_BUILD_LIBPROTOC"] = True
        if self._can_disable_rtti:
            cmake.definitions["protobuf_DISABLE_RTTI"] = not self.options.with_rtti
        if self._is_msvc or self._is_clang_cl:
            runtime = msvc_runtime_flag(self)
            if not runtime:
                runtime = self.settings.get_safe("compiler.runtime")
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in runtime
        if Version(self.version) < "3.18.0" and self._is_clang_cl:
            cmake.definitions["CMAKE_RC_COMPILER"] = os.environ.get("RC", "llvm-rc")
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Provide relocatable protobuf::protoc target and Protobuf_PROTOC_EXECUTABLE cache variable
        # TODO: some of the following logic might be disabled when conan will
        #       allow to create executable imported targets in package_info()
        protobuf_config_cmake = os.path.join(self._source_subfolder, "cmake", "protobuf-config.cmake.in")

        replace_in_file(self,
            protobuf_config_cmake,
            "@_protobuf_FIND_ZLIB@",
            "# BEGIN CONAN PATCH\n#_protobuf_FIND_ZLIB@\n# END CONAN PATCH"
        )

        exe_ext = ".exe" if self.settings.os == "Windows" else ""
        protoc_filename = "protoc" + exe_ext
        module_folder_depth = len(os.path.normpath(self._cmake_install_base_path).split(os.path.sep))
        protoc_rel_path = "{}bin/{}".format("".join(["../"] * module_folder_depth), protoc_filename)
        protoc_target = textwrap.dedent("""\
            if(NOT TARGET protobuf::protoc)
                if(CMAKE_CROSSCOMPILING)
                    find_program(PROTOC_PROGRAM protoc PATHS ENV PATH NO_DEFAULT_PATH)
                endif()
                if(NOT PROTOC_PROGRAM)
                    set(PROTOC_PROGRAM \"${{CMAKE_CURRENT_LIST_DIR}}/{protoc_rel_path}\")
                endif()
                get_filename_component(PROTOC_PROGRAM \"${{PROTOC_PROGRAM}}\" ABSOLUTE)
                set(Protobuf_PROTOC_EXECUTABLE ${{PROTOC_PROGRAM}} CACHE FILEPATH \"The protoc compiler\")
                add_executable(protobuf::protoc IMPORTED)
                set_property(TARGET protobuf::protoc PROPERTY IMPORTED_LOCATION ${{Protobuf_PROTOC_EXECUTABLE}})
            endif()
        """.format(protoc_rel_path=protoc_rel_path))
        replace_in_file(self,
            protobuf_config_cmake,
            "include(\"${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake\")",
            protoc_target
        )

        # Set DYLD_LIBRARY_PATH in command line to avoid issues with shared protobuf
        # (even with virtualrunenv, this fix might be required due to SIP)
        # Only works with cmake, cmake_find_package or cmake_find_package_multi generators
        if is_apple_os(self.settings.os):
            replace_in_file(self,
                protobuf_config_cmake,
                "add_custom_command(",
                ("set(CUSTOM_DYLD_LIBRARY_PATH ${CONAN_LIB_DIRS} ${Protobuf_LIB_DIRS} ${Protobuf_LIB_DIRS_RELEASE} ${Protobuf_LIB_DIRS_DEBUG} ${Protobuf_LIB_DIRS_RELWITHDEBINFO} ${Protobuf_LIB_DIRS_MINSIZEREL})\n"
                 "string(REPLACE \";\" \":\" CUSTOM_DYLD_LIBRARY_PATH \"${CUSTOM_DYLD_LIBRARY_PATH}\")\n"
                 "add_custom_command(")
            )
            cmd_str = "COMMAND  protobuf::protoc" if Version(self.version) < "3.20.0" else "COMMAND protobuf::protoc"
            replace_in_file(self,
                protobuf_config_cmake,
                cmd_str,
                "COMMAND ${CMAKE_COMMAND} -E env \"DYLD_LIBRARY_PATH=${CUSTOM_DYLD_LIBRARY_PATH}\" $<TARGET_FILE:protobuf::protoc>"
            )

        # Disable a potential warning in protobuf-module.cmake.in
        # TODO: remove this patch? Is it really useful?
        protobuf_module_cmake = os.path.join(self._source_subfolder, "cmake", "protobuf-module.cmake.in")
        replace_in_file(self,
            protobuf_module_cmake,
            "if(DEFINED Protobuf_SRC_ROOT_FOLDER)",
            "if(0)\nif(DEFINED Protobuf_SRC_ROOT_FOLDER)",
        )
        replace_in_file(self,
            protobuf_module_cmake,
            "# Define upper case versions of output variables",
            "endif()",
        )

        # https://github.com/protocolbuffers/protobuf/issues/9916
        # it will be solved in protobuf 3.21.0
        if Version(self.version) == "3.20.0":
            replace_in_file(self, os.path.join(self._source_subfolder, "src", "google", "protobuf", "port_def.inc"),
                "#elif PROTOBUF_GNUC_MIN(12, 0)",
                "#elif PROTOBUF_GNUC_MIN(12, 2)")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config-version.cmake"))
        os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-targets.cmake"))
        os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-targets-{}.cmake".format(str(self.settings.build_type).lower())))
        rename(self, os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config.cmake"),
                     os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-generate.cmake"))

        if not self.options.lite:
            rm(self, "libprotobuf-lite.*", os.path.join(self.package_folder, "lib"))
            rm(self, "libprotobuf-lite.*", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Protobuf")
        self.cpp_info.set_property("cmake_file_name", "protobuf")
        self.cpp_info.set_property("pkg_config_name", "protobuf_full_package") # unofficial, but required to avoid side effects (libprotobuf component "steals" the default global pkg_config name)

        build_modules = [
            os.path.join(self._cmake_install_base_path, "protobuf-generate.cmake"),
            os.path.join(self._cmake_install_base_path, "protobuf-module.cmake"),
            os.path.join(self._cmake_install_base_path, "protobuf-options.cmake"),
        ]
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        lib_prefix = "lib" if (self._is_msvc or self._is_clang_cl) else ""
        lib_suffix = "d" if self.settings.build_type == "Debug" and self.options.debug_suffix else ""

        # libprotobuf
        self.cpp_info.components["libprotobuf"].set_property("cmake_target_name", "protobuf::libprotobuf")
        self.cpp_info.components["libprotobuf"].set_property("pkg_config_name", "protobuf")
        self.cpp_info.components["libprotobuf"].builddirs.append(self._cmake_install_base_path)
        self.cpp_info.components["libprotobuf"].libs = [lib_prefix + "protobuf" + lib_suffix]
        if self.options.with_zlib:
            self.cpp_info.components["libprotobuf"].requires = ["zlib::zlib"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libprotobuf"].system_libs.append("pthread")
            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.components["libprotobuf"].system_libs.append("atomic")
        if self.settings.os == "Android":
            self.cpp_info.components["libprotobuf"].system_libs.append("log")
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.components["libprotobuf"].defines = ["PROTOBUF_USE_DLLS"]

        # libprotoc
        self.cpp_info.components["libprotoc"].set_property("cmake_target_name", "protobuf::libprotoc")
        self.cpp_info.components["libprotoc"].libs = [lib_prefix + "protoc" + lib_suffix]
        self.cpp_info.components["libprotoc"].requires = ["libprotobuf"]

        # libprotobuf-lite
        if self.options.lite:
            self.cpp_info.components["libprotobuf-lite"].set_property("cmake_target_name", "protobuf::libprotobuf-lite")
            self.cpp_info.components["libprotobuf-lite"].set_property("pkg_config_name", "protobuf-lite")
            self.cpp_info.components["libprotobuf-lite"].builddirs.append(self._cmake_install_base_path)
            self.cpp_info.components["libprotobuf-lite"].libs = [lib_prefix + "protobuf-lite" + lib_suffix]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libprotobuf-lite"].system_libs.append("pthread")
                if self._is_clang_x86 or "arm" in str(self.settings.arch):
                    self.cpp_info.components["libprotobuf-lite"].system_libs.append("atomic")
            if self.settings.os == "Windows":
                if self.options.shared:
                    self.cpp_info.components["libprotobuf-lite"].defines = ["PROTOBUF_USE_DLLS"]
            if self.settings.os == "Android":
                self.cpp_info.components["libprotobuf-lite"].system_libs.append("log")

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Protobuf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "protobuf"
        self.cpp_info.names["pkg_config"] ="protobuf_full_package"
        for generator in ["cmake_find_package", "cmake_find_package_multi"]:
            self.cpp_info.components["libprotobuf"].build_modules[generator] = build_modules
        if self.options.lite:
            for generator in ["cmake_find_package", "cmake_find_package_multi"]:
                self.cpp_info.components["libprotobuf-lite"].build_modules[generator] = build_modules

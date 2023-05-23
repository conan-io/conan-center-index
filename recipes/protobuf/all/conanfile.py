from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, rename, get, apply_conandata_patches, export_conandata_patches, replace_in_file, rmdir, rm
from conan.tools.microsoft import check_min_vs, msvc_runtime_flag, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

import os
import textwrap

required_conan_version = ">=1.53"


class ProtobufConan(ConanFile):
    name = "protobuf"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"
    package_type = "library"
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

    @property
    def _is_clang_cl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows"

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    @property
    def _can_disable_rtti(self):
        return Version(self.version) >= "3.15.4"

    @property
    def _min_cppstd(self):
        return 11 if Version(self.version) < "4.22.0" else 14

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "gcc": "8",
                "clang": "5",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._can_disable_rtti:
            del self.options.with_rtti

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if Version(self.version) >= "4.22.0":
            self.requires("abseil/20230125.3", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Protobuf can't be built with shared + MT(d) runtimes")

        if Version(self.version) < "4.22.0":
            check_min_vs(self, "190")
            if self.settings.compiler == "clang":
                if Version(self.version) >= "3.15.4" and Version(self.settings.compiler.version) < "4":
                    raise ConanInvalidConfiguration(f"{self.ref} doesn't support clang < 4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake", "protobuf")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_INSTALL_CMAKEDIR"] = self._cmake_install_base_path.replace("\\", "/")
        tc.cache_variables["protobuf_WITH_ZLIB"] = self.options.with_zlib
        tc.cache_variables["protobuf_BUILD_TESTS"] = False
        tc.cache_variables["protobuf_BUILD_PROTOC_BINARIES"] = self.settings.os != "tvOS"
        if not self.options.debug_suffix:
            tc.cache_variables["protobuf_DEBUG_POSTFIX"] = ""
        if Version(self.version) >= "3.14.0":
            tc.cache_variables["protobuf_BUILD_LIBPROTOC"] = self.settings.os != "tvOS"
        if self._can_disable_rtti:
            tc.cache_variables["protobuf_DISABLE_RTTI"] = not self.options.with_rtti
        if is_msvc(self) or self._is_clang_cl:
            runtime = msvc_runtime_flag(self)
            if not runtime:
                runtime = self.settings.get_safe("compiler.runtime")
            tc.cache_variables["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in runtime
        if is_apple_os(self) and self.options.shared:
            # Workaround against SIP on macOS for consumers while invoking protoc when protobuf lib is shared
            tc.variables["CMAKE_INSTALL_RPATH"] = "@loader_path/../lib"
        if Version(self.version) >= "4.22.0":
            tc.variables["protobuf_ABSL_PROVIDER"] = "package"
            tc.variables["CMAKE_CXX_STANDARD"] = 14
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Provide relocatable protobuf::protoc target and Protobuf_PROTOC_EXECUTABLE cache variable
        # TODO: some of the following logic might be disabled when conan will
        #       allow to create executable imported targets in package_info()
        protobuf_config_cmake = os.path.join(self.source_folder, "cmake", "protobuf-config.cmake.in")

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
                set(protobuf_PROTOC_EXE ${{PROTOC_PROGRAM}} CACHE FILEPATH \"The protoc compiler\")
                add_executable(protobuf::protoc IMPORTED)
                set_property(TARGET protobuf::protoc PROPERTY IMPORTED_LOCATION ${{Protobuf_PROTOC_EXECUTABLE}})
            endif()
        """.format(protoc_rel_path=protoc_rel_path))
        replace_in_file(self,
            protobuf_config_cmake,
            "include(\"${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake\")",
            protoc_target
        )

        # Disable a potential warning in protobuf-module.cmake.in
        # TODO: remove this patch? Is it really useful?
        protobuf_module_cmake = os.path.join(self.source_folder, "cmake", "protobuf-module.cmake.in")
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
            replace_in_file(self, os.path.join(self.source_folder, "src", "google", "protobuf", "port_def.inc"),
                "#elif PROTOBUF_GNUC_MIN(12, 0)",
                "#elif PROTOBUF_GNUC_MIN(12, 2)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake_root = "cmake" if Version(self.version) < "3.21" else None
        cmake.configure(build_script_folder=cmake_root)
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config-version.cmake"))
        if Version(self.version) < "4.22.0":
            os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-targets.cmake"))
            os.unlink(os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-targets-{}.cmake".format(str(self.settings.build_type).lower())))
            rename(self, os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config.cmake"),
                        os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-generate.cmake"))
        else:
            # TODO: diary hack, need to fix
            rename(self, os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config.cmake"),
                        os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-protoc.cmake"))

        if not self.options.lite:
            rm(self, "libprotobuf-lite*", os.path.join(self.package_folder, "lib"))
            rm(self, "libprotobuf-lite*", os.path.join(self.package_folder, "bin"))

        if Version(self.version) >= "4.22.0":
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake", "utf8_range"))

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
        if Version(self.version) >= "4.22.0":
            build_modules.append(os.path.join(self._cmake_install_base_path, "protobuf-protoc.cmake"))
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        lib_prefix = "lib" if (is_msvc(self) or self._is_clang_cl) else ""
        lib_suffix = "d" if self.settings.build_type == "Debug" and self.options.debug_suffix else ""

        if Version(self.version) >= "4.22.0":
            # utf8_range
            self.cpp_info.components["utf8_range"].set_property("cmake_target_name", "protobuf::utf8_range")
            self.cpp_info.components["utf8_range"].libs = [lib_prefix + "utf8_range"]
            # utf8_validity
            self.cpp_info.components["utf8_validity"].set_property("cmake_target_name", "protobuf::utf8_validity")
            self.cpp_info.components["utf8_validity"].libs = [lib_prefix + "utf8_validity"]

        # libprotobuf
        self.cpp_info.components["libprotobuf"].set_property("cmake_target_name", "protobuf::libprotobuf")
        self.cpp_info.components["libprotobuf"].set_property("pkg_config_name", "protobuf")
        self.cpp_info.components["libprotobuf"].builddirs.append(self._cmake_install_base_path)
        self.cpp_info.components["libprotobuf"].libs = [lib_prefix + "protobuf" + lib_suffix]
        if self.options.with_zlib:
            self.cpp_info.components["libprotobuf"].requires = ["zlib::zlib"]
        if Version(self.version) >= "4.22.0":
            self.cpp_info.components["libprotobuf"].requires.extend(["abseil::abseil", "utf8_range", "utf8_validity"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libprotobuf"].system_libs.extend(["m", "pthread"])
            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.components["libprotobuf"].system_libs.append("atomic")
        if self.settings.os == "Android":
            self.cpp_info.components["libprotobuf"].system_libs.append("log")
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.components["libprotobuf"].defines = ["PROTOBUF_USE_DLLS"]

        # libprotoc
        if self.settings.os != "tvOS":
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
                self.cpp_info.components["libprotobuf-lite"].system_libs.extend(["m", "pthread"])
                if self._is_clang_x86 or "arm" in str(self.settings.arch):
                    self.cpp_info.components["libprotobuf-lite"].system_libs.append("atomic")
            if self.settings.os == "Windows":
                if self.options.shared:
                    self.cpp_info.components["libprotobuf-lite"].defines = ["PROTOBUF_USE_DLLS"]
            if self.settings.os == "Android":
                self.cpp_info.components["libprotobuf-lite"].system_libs.append("log")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Protobuf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "protobuf"
        self.cpp_info.names["pkg_config"] ="protobuf_full_package"
        for generator in ["cmake_find_package", "cmake_find_package_multi"]:
            self.cpp_info.components["libprotobuf"].build_modules[generator] = build_modules
        if self.options.lite:
            for generator in ["cmake_find_package", "cmake_find_package_multi"]:
                self.cpp_info.components["libprotobuf-lite"].build_modules[generator] = build_modules
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

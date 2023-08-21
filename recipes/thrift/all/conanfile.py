from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class ThriftConan(ConanFile):
    name = "thrift"
    description = "Thrift is an associated code generation mechanism for RPC"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/thrift"
    topics = ("thrift", "serialization", "rpc")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_libevent": [True, False],
        "with_openssl": [True, False],
        "with_c_glib": [True, False],
        "with_cpp": [True, False],
        "with_java": [True, False],
        "with_python": [True, False],
        "with_qt5": [True, False],
        "with_haskell": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_libevent": True,
        "with_openssl": True,
        "with_c_glib": False,
        "with_cpp": True,
        "with_java": False,
        "with_python": False,
        "with_qt5": False,
        "with_haskell": False,
    }

    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.82.0", transitive_headers=True)
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_qt5:
            self.requires("qt/5.15.9")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        for option, value in self.options.items():
            if option.startswith("with_"):
                tc.variables[option.upper()] = value
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_COMPILER"] = True
        tc.variables["BUILD_LIBRARIES"] = True
        tc.variables["BUILD_TUTORIALS"] = False
        if is_msvc(self):
            tc.variables["WITH_MT"] = is_msvc_static_runtime(self)
        # This policy doesn't matter for us, but avoids a warning
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0074"] = "NEW"
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

        env = VirtualBuildEnv(self)
        env.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)
        # No static code analysis (seems to trigger CMake warnings due to weird custom Find module file)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "include(StaticCodeAnalysis)", "")
        # TODO: To remove in conan v2, but it's still needed if building with 1 profile.
        #       May also be removed if flex & bison recipes define cmake_find_mode property to "none" in their package_info()
        for f in ["Findflex.cmake", "flex-config.cmake", "Findbison.cmake", "bison-config.cmake"]:
            rm(self, f, self.generators_folder)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Copy generated headers from build tree
        copy(self, "*.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include"), keep_path=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        targets = {}
        if self.options.with_zlib:
            targets.update({"thriftz::thriftz": "thrift::thriftz"})
        if self.options.with_libevent:
            targets.update({"thriftnb::thriftnb": "thrift::thriftnb"})
        if self.options.with_qt5:
            targets.update({"thriftqt5::thriftqt5": "thrift::thriftqt5"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Thrift")
        # unofficial, for conan internal purpose, it avoids conflict with libthrift component
        self.cpp_info.set_property("cmake_target_name", "thrift::thrift-conan-do-not-use")
        self.cpp_info.set_property("pkg_config_name", "thrift_conan_do_not_use")

        libsuffix = "{}{}".format(
            ("mt" if is_msvc_static_runtime(self) else "md") if is_msvc(self) else "",
            "d" if self.settings.build_type == "Debug" else "",
        )

        self.cpp_info.components["libthrift"].set_property("cmake_target_name", "thrift::thrift")
        self.cpp_info.components["libthrift"].set_property("pkg_config_name", "thrift")
        self.cpp_info.components["libthrift"].libs = [f"thrift{libsuffix}"]
        if self.settings.os == "Windows":
            self.cpp_info.components["libthrift"].defines.append("NOMINMAX")
            if Version(self.version) >= "0.15.0":
                self.cpp_info.components["libthrift"].system_libs.append("shlwapi")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libthrift"].system_libs.extend(["m", "pthread"])
        self.cpp_info.components["libthrift"].requires.append("boost::headers")
        if self.options.with_openssl:
            self.cpp_info.components["libthrift"].requires.append("openssl::openssl")

        if self.options.with_zlib:
            self.cpp_info.components["libthrift_z"].set_property("cmake_target_name", "thriftz::thriftz")
            self.cpp_info.components["libthrift_z"].set_property("pkg_config_name", "thrift-z")
            self.cpp_info.components["libthrift_z"].libs = [f"thriftz{libsuffix}"]
            self.cpp_info.components["libthrift_z"].requires = ["libthrift", "zlib::zlib"]


        if self.options.with_libevent:
            self.cpp_info.components["libthrift_nb"].set_property("cmake_target_name", "thriftnb::thriftnb")
            self.cpp_info.components["libthrift_nb"].set_property("pkg_config_name", "thrift-nb")
            self.cpp_info.components["libthrift_nb"].libs = [f"thriftnb{libsuffix}"]
            self.cpp_info.components["libthrift_nb"].requires = ["libthrift", "libevent::libevent"]

        if self.options.with_qt5:
            self.cpp_info.components["libthrift_qt5"].set_property("cmake_target_name", "thriftqt5::thriftqt5")
            self.cpp_info.components["libthrift_qt5"].set_property("pkg_config_name", "thrift-qt5")
            self.cpp_info.components["libthrift_qt5"].libs = [f"thriftqt5{libsuffix}"]
            self.cpp_info.components["libthrift_qt5"].requires = ["libthrift", "qt::qtCore"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var with : {bin_path}")
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Thrift"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Thrift"
        self.cpp_info.names["cmake_find_package"] = "thrift"
        self.cpp_info.names["cmake_find_package_multi"] = "thrift"
        self.cpp_info.names["pkg_config"] = "thrift_conan_do_not_use"
        self.cpp_info.components["libthrift"].names["cmake_find_package"] = "thrift"
        self.cpp_info.components["libthrift"].names["cmake_find_package_multi"] = "thrift"
        if self.options.with_zlib:
            self.cpp_info.components["libthrift_z"].names["cmake_find_package"] = "thriftz"
            self.cpp_info.components["libthrift_z"].names["cmake_find_package_multi"] = "thriftz"
            self.cpp_info.components["libthrift_z"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["libthrift_z"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_libevent:
            self.cpp_info.components["libthrift_nb"].names["cmake_find_package"] = "thriftnb"
            self.cpp_info.components["libthrift_nb"].names["cmake_find_package_multi"] = "thriftnb"
            self.cpp_info.components["libthrift_nb"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["libthrift_nb"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_qt5:
            self.cpp_info.components["libthrift_qt5"].names["cmake_find_package"] = "thriftqt5"
            self.cpp_info.components["libthrift_qt5"].names["cmake_find_package_multi"] = "thriftqt5"
            self.cpp_info.components["libthrift_qt5"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["libthrift_qt5"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

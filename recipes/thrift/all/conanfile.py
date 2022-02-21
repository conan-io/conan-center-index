from conans import tools, CMake, ConanFile
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">1.43.0"


class ThriftConan(ConanFile):
    name = "thrift"
    description = "Thrift is an associated code generation mechanism for RPC"
    topics = ("thrift", "serialization", "rpc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/thrift"
    license = "Apache-2.0"

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
        "with_qt": [True, False],
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
        "with_qt": False,
        "with_haskell": False,
    }

    short_paths = True
    generators = "cmake", "cmake_find_package"
    _cmake = None

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
    def _is_vc_static_runtime(self):
        return (self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime) or \
               (str(self.settings.compiler) == "msvc" and self.settings.compiler.runtime == "static")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1m")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")

    def validate(self):
        if self.options.with_qt:
            # FIXME: missing qt recipe
            raise ConanInvalidConfiguration("qt is not (yet) available on cci")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.7.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        for option, value in self.options.items():
            if option.startswith("with_"):
                self._cmake.definitions[option.upper()] = value

        self._cmake.definitions["WITH_SHARED_LIB"] = self.options.shared
        self._cmake.definitions["WITH_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["BOOST_ROOT"] = self.deps_cpp_info["boost"].rootpath
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_COMPILER"] = True
        self._cmake.definitions["BUILD_LIBRARIES"] = True
        self._cmake.definitions["BUILD_TUTORIALS"] = False

        if self._is_msvc:
            self._cmake.definitions["WITH_MT"] = self._is_vc_static_runtime

        # Make optional libs "findable"
        if self.options.with_openssl:
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        if self.options.with_zlib:
            self._cmake.definitions["ZLIB_ROOT"] = self.deps_cpp_info["zlib"].rootpath
        if self.options.with_libevent:
            self._cmake.definitions["LIBEVENT_ROOT"] = self.deps_cpp_info["libevent"].rootpath

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        for f in ["Findflex.cmake", "Findbison.cmake"]:
            if os.path.isfile(f):
                os.unlink(f)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # Copy generated headers from build tree
        build_source_dir = os.path.join(self._build_subfolder, self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=build_source_dir, keep_path=True)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        targets = {"thriftnb::thriftnb": "thrift::thriftnb"}
        if self.options.with_zlib:
            targets.update({"thriftz::thriftz": "thrift::thriftz"})
        if self.options.with_qt:
            targets.update({"thriftqt5::thriftqt5": "thrift::thriftqt5"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Thrift")
        # unofficial, for conan internal purpose, it avoids conflict with libthrift component
        self.cpp_info.set_property("cmake_target_name", "thrift::thrift-conan-do-not-use")
        self.cpp_info.set_property("pkg_config_name", "thrift_conan_do_not_use")

        libsuffix = "{}{}".format(
            ("mt" if self._is_vc_static_runtime else "md") if self._is_msvc else "",
            "d" if self.settings.build_type == "Debug" else "",
        )

        self.cpp_info.components["libthrift"].set_property("cmake_target_name", "thrift::thrift")
        self.cpp_info.components["libthrift"].set_property("pkg_config_name", "thrift")
        self.cpp_info.components["libthrift"].libs = ["thrift" + libsuffix]
        if self.settings.os == "Windows":
            self.cpp_info.components["libthrift"].defines.append("NOMINMAX")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libthrift"].system_libs.extend(["m", "pthread"])
        self.cpp_info.components["libthrift"].requires.append("boost::headers")
        if self.options.with_openssl:
            self.cpp_info.components["libthrift"].requires.append("openssl::openssl")
        if self.options.with_libevent:
            self.cpp_info.components["libthrift"].requires.append("libevent::libevent")

        if self.options.with_zlib:
            self.cpp_info.components["libthrift_z"].set_property("cmake_target_name", "thriftz::thriftz")
            self.cpp_info.components["libthrift_z"].set_property("pkg_config_name", "thrift-z")
            self.cpp_info.components["libthrift_z"].libs = ["thriftz" + libsuffix]
            self.cpp_info.components["libthrift_z"].requires = ["libthrift", "zlib::zlib"]

        self.cpp_info.components["libthrift_nb"].set_property("cmake_target_name", "thriftnb::thriftnb")
        self.cpp_info.components["libthrift_nb"].set_property("pkg_config_name", "thrift-nb")
        self.cpp_info.components["libthrift_nb"].libs = ["thriftnb" + libsuffix]
        self.cpp_info.components["libthrift_nb"].requires = ["libthrift"]

        if self.options.with_qt:
            self.cpp_info.components["libthrift_qt5"].set_property("cmake_target_name", "thriftqt5::thriftqt5")
            self.cpp_info.components["libthrift_qt5"].set_property("pkg_config_name", "thrift-qt5")
            self.cpp_info.components["libthrift_qt5"].libs = ["thriftqt5" + libsuffix]
            self.cpp_info.components["libthrift_qt5"].requires = ["libthrift", "qt::core"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
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
        self.cpp_info.components["libthrift_nb"].names["cmake_find_package"] = "thriftnb"
        self.cpp_info.components["libthrift_nb"].names["cmake_find_package_multi"] = "thriftnb"
        self.cpp_info.components["libthrift_nb"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libthrift_nb"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_qt:
            self.cpp_info.components["libthrift_qt5"].names["cmake_find_package"] = "thriftqt5"
            self.cpp_info.components["libthrift_qt5"].names["cmake_find_package_multi"] = "thriftqt5"
            self.cpp_info.components["libthrift_qt5"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["libthrift_qt5"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

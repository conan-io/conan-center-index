from conans import tools, CMake, ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import textwrap
import functools

required_conan_version = ">1.43.0"


class ThriftConan(ConanFile):
    name = "thrift"
    description = "Thrift is an associated code generation mechanism for RPC"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/thrift"
    topics = ("thrift", "serialization", "rpc")
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
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        self.requires("boost/1.79.0")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1o")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_qt5:
            self.requires("qt/5.15.4")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.7.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        for option, value in self.options.items():
            if option.startswith("with_"):
                cmake.definitions[option.upper()] = value

        cmake.definitions["BOOST_ROOT"] = self.deps_cpp_info["boost"].rootpath
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["BUILD_COMPILER"] = True
        cmake.definitions["BUILD_LIBRARIES"] = True
        cmake.definitions["BUILD_TUTORIALS"] = False

        if is_msvc(self):
            cmake.definitions["WITH_MT"] = is_msvc_static_runtime(self)

        # Make optional libs "findable"
        if self.options.with_openssl:
            cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        if self.options.with_zlib:
            cmake.definitions["ZLIB_ROOT"] = self.deps_cpp_info["zlib"].rootpath
        cmake.definitions["WITH_LIBEVENT"] = self.options.with_libevent
        if self.options.with_libevent:
            cmake.definitions["LIBEVENT_ROOT"] = self.deps_cpp_info["libevent"].rootpath

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

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
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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
            ("mt" if is_msvc_static_runtime(self) else "md") if is_msvc(self) else "",
            "d" if self.settings.build_type == "Debug" else "",
        )

        self.cpp_info.components["libthrift"].set_property("cmake_target_name", "thrift::thrift")
        self.cpp_info.components["libthrift"].set_property("pkg_config_name", "thrift")
        self.cpp_info.components["libthrift"].libs = ["thrift" + libsuffix]
        if self.settings.os == "Windows":
            self.cpp_info.components["libthrift"].defines.append("NOMINMAX")
            if tools.Version(self.version) >= "0.15.0":
                self.cpp_info.components["libthrift"].system_libs.append("shlwapi")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libthrift"].system_libs.extend(["m", "pthread"])
        self.cpp_info.components["libthrift"].requires.append("boost::headers")
        if self.options.with_openssl:
            self.cpp_info.components["libthrift"].requires.append("openssl::openssl")
        self.cpp_info.components["libthrift"].builddirs = [os.path.join("lib", "cmake")]

        if self.options.with_zlib:
            self.cpp_info.components["libthrift_z"].set_property("cmake_target_name", "thriftz::thriftz")
            self.cpp_info.components["libthrift_z"].set_property("pkg_config_name", "thrift-z")
            self.cpp_info.components["libthrift_z"].libs = ["thriftz" + libsuffix]
            self.cpp_info.components["libthrift_z"].requires = ["libthrift", "zlib::zlib"]


        if self.options.with_libevent:
            self.cpp_info.components["libthrift_nb"].set_property("cmake_target_name", "thriftnb::thriftnb")
            self.cpp_info.components["libthrift_nb"].set_property("pkg_config_name", "thrift-nb")
            self.cpp_info.components["libthrift_nb"].libs = ["thriftnb" + libsuffix]
            self.cpp_info.components["libthrift_nb"].requires = ["libthrift", "libevent::libevent"]

        if self.options.with_qt5:
            self.cpp_info.components["libthrift_qt5"].set_property("cmake_target_name", "thriftqt5::thriftqt5")
            self.cpp_info.components["libthrift_qt5"].set_property("pkg_config_name", "thrift-qt5")
            self.cpp_info.components["libthrift_qt5"].libs = ["thriftqt5" + libsuffix]
            self.cpp_info.components["libthrift_qt5"].requires = ["libthrift", "qt::qtCore"]

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

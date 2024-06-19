import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class DCMTKConan(ConanFile):
    name = "dcmtk"
    description = "DCMTK is a collection of libraries and applications implementing large parts the DICOM standard"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dicom.offis.de/dcmtk"
    license = "BSD-3-Clause"
    topics = ("dicom", "image")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_applications": [True, False],
        "with_multithreading": [True, False],
        "charset_conversion": [None, "libiconv", "icu"],
        "with_libxml2": [True, False],
        "with_zlib": [True, False],
        "with_openssl": [True, False],
        "with_libpng": [True, False],
        "with_libtiff": [True, False],
        "with_tcpwrappers": [True, False],
        "default_dict": ["builtin", "external", "none"],
        "builtin_dictionary": [None, True, False, "deprecated"],
        "use_dcmdictpath": [True, False],
        "builtin_private_tags": [True, False],
        "external_dictionary": [None, True, False, "deprecated"],
        "wide_io": [True, False],
        "enable_stl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_applications": False,
        "with_multithreading": True,
        "charset_conversion": "libiconv",
        "with_libxml2": True,
        "with_zlib": True,
        "with_openssl": True,
        "with_libpng": True,
        "with_libtiff": True,
        "with_tcpwrappers": False,
        "default_dict": "external",
        "builtin_dictionary": "deprecated",
        "use_dcmdictpath": True,
        "builtin_private_tags": False,
        "external_dictionary": "deprecated",
        "wide_io": False,
        "enable_stl": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("with_tcpwrappers")
            self.options.default_dict = "builtin"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # Deprecated options
        if self.options.builtin_dictionary != "deprecated":
            self.output.warning("builtin_dictionary option is deprecated. Use default_dict option instead.")
            if self.options.builtin_dictionary:
                self.options.default_dict = "builtin"
            elif self.options.builtin_dictionary == False:
                self.options.default_dict = "external"
        if self.options.external_dictionary != "deprecated":
            self.output.warning("external_dictionary option is deprecated. Use use_dcmdictpath option instead.")
            if self.options.external_dictionary:
                self.options.use_dcmdictpath = True
            elif self.options.external_dictionary == False:
                self.options.use_dcmdictpath = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.charset_conversion == "libiconv":
            self.requires("libiconv/1.17")
        elif self.options.charset_conversion == "icu":
            self.requires("icu/73.2")
        if self.options.with_libxml2:
            self.requires("libxml2/2.11.4")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_openssl:
            self.requires("openssl/[>=1 <4]")
        if self.options.with_libpng:
            self.requires("libpng/1.6.40")
        if self.options.with_libtiff:
            self.requires("libtiff/4.6.0")
        if self.options.get_safe("with_tcpwrappers"):
            self.requires("tcp-wrappers/7.6")

    def package_id(self):
        # Deprecated options don't contribute to package id
        del self.info.options.builtin_dictionary
        del self.info.options.external_dictionary

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if hasattr(self, "settings_build") and cross_building(self) and self.settings.os == "Macos":
            # FIXME: Probable issue with flags, build includes header 'mmintrin.h'
            raise ConanInvalidConfiguration("Cross building on Macos is not supported (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # DICOM Data Dictionaries are required
        tc.variables["CMAKE_INSTALL_DATADIR"] = self._dcm_datadictionary_path.replace("\\", "/")
        tc.cache_variables["DCMTK_USE_FIND_PACKAGE"] = True
        tc.variables["BUILD_APPS"] = self.options.with_applications
        tc.variables["DCMTK_WITH_TIFF"] = self.options.with_libtiff
        tc.variables["DCMTK_WITH_PNG"] = self.options.with_libpng
        tc.variables["DCMTK_WITH_XML"] = self.options.with_libxml2
        tc.variables["DCMTK_WITH_ZLIB"] = self.options.with_zlib
        tc.variables["DCMTK_WITH_OPENSSL"] = self.options.with_openssl
        tc.variables["DCMTK_WITH_SNDFILE"] = False # not used at all, do not try to add an option for this one
        tc.variables["DCMTK_WITH_ICONV"] = self.options.charset_conversion == "libiconv"
        tc.variables["DCMTK_WITH_ICU"] = self.options.charset_conversion == "icu"
        if self.settings.os != "Windows":
            tc.variables["DCMTK_WITH_WRAP"] = self.options.with_tcpwrappers
        tc.variables["DCMTK_WITH_OPENJPEG"] = False # not used at all, do not try to add an option for this one
        tc.variables["DCMTK_ENABLE_PRIVATE_TAGS"] = self.options.builtin_private_tags
        tc.variables["DCMTK_WITH_THREADS"] = self.options.with_multithreading
        tc.variables["DCMTK_WITH_DOXYGEN"] = False
        tc.variables["DCMTK_WIDE_CHAR_FILE_IO_FUNCTIONS"] = self.options.wide_io
        tc.variables["DCMTK_WIDE_CHAR_MAIN_FUNCTION"] = self.options.wide_io
        # Upstream CMakeLists really expects ON value and no other value (like TRUE) in its internal logic
        # to enable STL features (see DCMTK_TEST_ENABLE_STL_FEATURE() function in CMake/GenerateDCMTKConfigure.cmake)
        tc.variables["DCMTK_ENABLE_STL"] = "ON" if self.options.enable_stl else "OFF"
        tc.variables["DCMTK_ENABLE_CXX11"] = True
        tc.variables["DCMTK_ENABLE_MANPAGE"] = False
        tc.cache_variables["DCMTK_DEFAULT_DICT"] = self.options.default_dict
        tc.variables["DCMTK_USE_DCMDICTPATH"] = self.options.use_dcmdictpath
        if self.settings.os == "Windows":
            tc.variables["DCMTK_OVERWRITE_WIN32_COMPILER_FLAGS"] = False
        if is_msvc(self):
            tc.variables["DCMTK_ICONV_FLAGS_ANALYZED"] = True
            tc.variables["DCMTK_COMPILE_WIN32_MULTITHREADED_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _collect_cmake_required(self, host_dependency):
        """
        Collect all compile & link flags of a host dependency so that they can be used in:
          - CMAKE_REQUIRED_FLAGS
          - CMAKE_REQUIRED_INCLUDES
          - CMAKE_REQUIRED_DEFINITIONS
          - CMAKE_REQUIRED_LINK_OPTIONS
          - CMAKE_REQUIRED_LIBRARIES
        These variables are listened by CMake functions like check_symbol_exists() etc
        """
        # Aggregate cpp_info of dependency and all its depencencies (direct and transitive)
        dep = self.dependencies.host[host_dependency]
        dep_cpp_info = dep.cpp_info.aggregated_components()
        for _, trans_dep in dep.dependencies.items():
            if trans_dep.context == "host":
                dep_cpp_info.merge(trans_dep.cpp_info.aggregated_components())

        dep_includes = [p.replace("\\", "/") for p in dep_cpp_info.includedirs]
        libdirs_flag = "/LIBPATH:" if is_msvc(self) else "-L"
        dep_libdirs = ["{}{}".format(libdirs_flag, p.replace("\\", "/")) for p in dep_cpp_info.libdirs]
        dep_frameworks = [f"-framework {f}" for f in dep_cpp_info.frameworks]

        return {
            "flags": ";".join(dep_cpp_info.cflags + dep_cpp_info.cxxflags),
            "includes": ";".join(dep_includes),
            "definitions": ";".join(dep_cpp_info.defines),
            "link_options": ";".join(dep_libdirs + dep_cpp_info.exelinkflags + dep_frameworks),
            "libraries": ";".join(dep_cpp_info.libs + dep_cpp_info.system_libs),
        }

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Workaround for CMakeDeps bug with check_* like functions.
        # See https://github.com/conan-io/conan/issues/12012 & https://github.com/conan-io/conan/issues/12180
        if self.options.with_openssl:
            cmake_required = self._collect_cmake_required("openssl")
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMake", "dcmtkPrepare.cmake"),
                "set(CMAKE_REQUIRED_LIBRARIES ${CMAKE_REQUIRED_LIBRARIES} ${OPENSSL_LIBS} ${THREAD_LIBS})",
                textwrap.dedent(f"""\
                    list(APPEND CMAKE_REQUIRED_FLAGS "{cmake_required['flags']}")
                    list(APPEND CMAKE_REQUIRED_INCLUDES "{cmake_required['includes']}")
                    list(APPEND CMAKE_REQUIRED_DEFINITIONS "{cmake_required['definitions']}")
                    list(APPEND CMAKE_REQUIRED_LINK_OPTIONS "{cmake_required['link_options']}")
                    list(APPEND CMAKE_REQUIRED_LIBRARIES "{cmake_required['libraries']}")
                """),
            )

        if self.options.charset_conversion == "libiconv":
            cmake_required = self._collect_cmake_required("libiconv")
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMake", "3rdparty.cmake"),
                "set(CMAKE_REQUIRED_LIBRARIES ${LIBICONV_LIBS})",
                textwrap.dedent(f"""\
                    list(APPEND CMAKE_REQUIRED_FLAGS "{cmake_required['flags']}")
                    list(APPEND CMAKE_REQUIRED_DEFINITIONS "{cmake_required['definitions']}")
                    list(APPEND CMAKE_REQUIRED_LINK_OPTIONS "{cmake_required['link_options']}")
                    list(APPEND CMAKE_REQUIRED_LIBRARIES "{cmake_required['libraries']}")
                """),
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove once support of cmake_find_package* dropped
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {target: f"DCMTK::{target}" for target in self._dcmtk_components}
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

    @property
    def _dcmtk_components(self):
        def charset_conversion():
            if bool(self.options.charset_conversion):
                return ["libiconv::libiconv"] if self.options.charset_conversion == "libiconv" else ["icu::icu"]
            return []

        def zlib():
            return ["zlib::zlib"] if self.options.with_zlib else []

        def png():
            return ["libpng::libpng"] if self.options.with_libpng else []

        def tiff():
            return ["libtiff::libtiff"] if self.options.with_libtiff else []

        def openssl():
            return ["openssl::openssl"] if self.options.with_openssl else []

        def tcpwrappers():
            return ["tcp-wrappers::tcp-wrappers"] if self.options.get_safe("with_tcpwrappers") else []

        def xml2():
            return ["libxml2::libxml2"] if self.options.with_libxml2 else []

        components = {
            "ofstd"   : charset_conversion(),
            "oflog"   : ["ofstd"],
            "dcmdata" : ["ofstd", "oflog"] + zlib(),
            "i2d"     : ["dcmdata"],
            "dcmimgle": ["ofstd", "oflog", "dcmdata"],
            "dcmimage": ["oflog", "dcmdata", "dcmimgle"] + png() + tiff(),
            "dcmjpeg" : ["ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage", "ijg8", "ijg12", "ijg16"],
            "ijg8"    : [],
            "ijg12"   : [],
            "ijg16"   : [],
            "dcmjpls" : ["ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage", "dcmtkcharls"],
            "dcmtkcharls": ["ofstd", "oflog"],
            "dcmtls"  : ["ofstd", "dcmdata", "dcmnet"] + openssl(),
            "dcmnet"  : ["ofstd", "oflog", "dcmdata"] + tcpwrappers(),
            "dcmsr"   : ["ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage"] + xml2(),
            "cmr"     : ["dcmsr"],
            "dcmdsig" : ["ofstd", "dcmdata"] + openssl(),
            "dcmwlm"  : ["ofstd", "dcmdata", "dcmnet"],
            "dcmqrdb" : ["ofstd", "dcmdata", "dcmnet"],
            "dcmpstat": ["ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage", "dcmnet", "dcmdsig", "dcmtls", "dcmsr", "dcmqrdb"] + openssl(),
            "dcmrt"   : ["ofstd", "oflog", "dcmdata", "dcmimgle"],
            "dcmiod"  : ["dcmdata", "ofstd", "oflog"],
            "dcmfg"   : ["dcmiod", "dcmdata", "ofstd", "oflog"],
            "dcmseg"  : ["dcmfg", "dcmiod", "dcmdata", "ofstd", "oflog"],
            "dcmtract": ["dcmiod", "dcmdata", "ofstd", "oflog"],
            "dcmpmap" : ["dcmfg", "dcmiod", "dcmdata", "ofstd", "oflog"],
            "dcmect"  : ["dcmfg", "dcmiod", "dcmdata", "ofstd", "oflog"],
        }
        if Version(self.version) >= "3.6.8":
            components["dcmxml"] = ["dcmdata", "ofstd", "oflog"] + zlib() + xml2()
            components["oficonv"] = []
            components["dcmpstat"] += ["dcmiod"]
            components["i2d"] += ["dcmxml"]
            components["ofstd"] += ["oficonv"]
        return components

    @property
    def _dcm_datadictionary_path(self):
        return os.path.join(self.package_folder, "bin", "share")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "DCMTK")

        for target_lib, requires in self._dcmtk_components.items():
            self.cpp_info.components[target_lib].set_property("cmake_target_name", f"DCMTK::{target_lib}")
            # Before 3.6.7, targets were not namespaced, therefore they are also exposed for convenience
            self.cpp_info.components[target_lib].set_property("cmake_target_aliases", [target_lib])

            self.cpp_info.components[target_lib].libs = [target_lib]
            self.cpp_info.components[target_lib].includedirs.append(os.path.join("include", "dcmtk"))
            self.cpp_info.components[target_lib].requires = requires

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[target_lib].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[target_lib].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

            if is_msvc(self):
                # Required for the __cplusplus check at
                # https://github.com/DCMTK/dcmtk/blob/DCMTK-3.6.8/config/include/dcmtk/config/osconfig.h.in#L1489
                self.cpp_info.components[target_lib].cxxflags.append("/Zc:__cplusplus")

        system_libs = []
        if self.settings.os == "Windows":
            system_libs = ["iphlpapi", "ws2_32", "netapi32", "wsock32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            system_libs = ["m", "nsl"]
            if self.options.with_multithreading:
                system_libs.append("pthread")
            if Version(self.version) >= "3.6.8":
                system_libs.append("rt")
        if Version(self.version) >= "3.6.8":
            self.cpp_info.components["oficonv"].system_libs = system_libs
        else:
            self.cpp_info.components["ofstd"].system_libs = system_libs

        if self.options.default_dict == "external":
            dcmdictpath = os.path.join(self._dcm_datadictionary_path, "dcmtk", "dicom.dic")
            self.runenv_info.define_path("DCMDICTPATH", dcmdictpath)
            if self.options.with_applications:
                self.buildenv_info.define_path("DCMDICTPATH", dcmdictpath)

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "DCMTK"
        self.cpp_info.names["cmake_find_package_multi"] = "DCMTK"
        if self.options.default_dict == "external":
            self.env_info.DCMDICTPATH = dcmdictpath
        if self.options.with_applications:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

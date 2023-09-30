import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

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
        "builtin_dictionary": [None, True, False],
        "builtin_private_tags": [True, False],
        "external_dictionary": [None, True, False],
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
        "builtin_dictionary": None,
        "builtin_private_tags": False,
        "external_dictionary": None,
        "wide_io": False,
        "enable_stl": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("with_tcpwrappers")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

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

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self) and \
           self.settings.os == "Macos" and self.settings.arch == "armv8":
            # FIXME: Probable issue with flags, build includes header 'mmintrin.h'
            raise ConanInvalidConfiguration("Cross building to Macos M1 is not supported (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # DICOM Data Dictionaries are required
        tc.variables["CMAKE_INSTALL_DATADIR"] = self._dcm_datadictionary_path
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
        tc.variables["DCMTK_ENABLE_STL"] = self.options.enable_stl
        tc.variables["DCMTK_ENABLE_CXX11"] = True
        tc.variables["DCMTK_ENABLE_MANPAGE"] = False
        if self.options.external_dictionary is not None:
            tc.variables["DCMTK_DEFAULT_DICT"] = self.options.external_dictionary
        if self.options.builtin_dictionary is not None:
            tc.variables["DCMTK_ENABLE_BUILTIN_DICTIONARY"] = self.options.builtin_dictionary
        if self.settings.os == "Windows":
            tc.variables["DCMTK_OVERWRITE_WIN32_COMPILER_FLAGS"] = False
        if is_msvc(self):
            tc.variables["DCMTK_ICONV_FLAGS_ANALYZED"] = True
            tc.variables["DCMTK_COMPILE_WIN32_MULTITHREADED_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        if self.options.with_openssl:
            # Workaround for CMakeDeps bug
            # see https://github.com/conan-io/conan/issues/12012 & https://github.com/conan-io/conan/issues/12180
            openssl = self.dependencies["openssl"]
            openssl_cpp_info = openssl.cpp_info.aggregated_components()
            openssl_includes = [p.replace("\\", "/") for p in openssl_cpp_info.includedirs]
            openssl_defs = [d for d in openssl_cpp_info.defines]
            openssl_libdirs = ["-L{}".format(p.replace("\\", "/")) for p in openssl_cpp_info.libdirs]
            openssl_libs = [l for l in openssl_cpp_info.libs]
            openssl_system_libs = [s for s in openssl_cpp_info.system_libs]
            openssl_frameworks = [f"-framework {f}" for f in openssl_cpp_info.frameworks]
            for dep, _ in openssl.dependencies.items():
                openssl_dep_cpp_info = self.dependencies[dep.ref.name].cpp_info.aggregated_components()
                openssl_includes.extend([p.replace("\\", "/") for p in openssl_dep_cpp_info.includedirs])
                openssl_defs.extend(d for d in openssl_dep_cpp_info.defines)
                openssl_libdirs.extend(["-L{}".format(p.replace("\\", "/")) for p in openssl_dep_cpp_info.libdirs])
                openssl_libs.extend([l for l in openssl_dep_cpp_info.libs])
                openssl_system_libs.extend([s for s in openssl_dep_cpp_info.system_libs])
                openssl_frameworks.extend([f"-framework {f}" for f in openssl_dep_cpp_info.frameworks])

            cmake_required_includes = ";".join(openssl_includes)
            cmake_required_definitions = ";".join(openssl_defs)
            cmake_required_link_options = ";".join(openssl_libdirs + openssl_frameworks)
            cmake_required_libraries = ";".join(openssl_libs + openssl_system_libs)
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMake", "dcmtkPrepare.cmake"),
                "set(CMAKE_REQUIRED_LIBRARIES ${CMAKE_REQUIRED_LIBRARIES} ${OPENSSL_LIBS} ${THREAD_LIBS})",
                textwrap.dedent(f"""\
                    list(APPEND CMAKE_REQUIRED_INCLUDES "{cmake_required_includes}")
                    list(APPEND CMAKE_REQUIRED_DEFINITIONS "{cmake_required_definitions}")
                    list(APPEND CMAKE_REQUIRED_LINK_OPTIONS "{cmake_required_link_options}")
                    list(APPEND CMAKE_REQUIRED_LIBRARIES "{cmake_required_libraries}")
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
            {target: f"dcmtk::{target}" for target in self._dcmtk_components}
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

        return {
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
        }

    @property
    def _dcm_datadictionary_path(self):
        return os.path.join(self.package_folder, "bin", "share")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "DCMTK")

        for target_lib, requires in self._dcmtk_components.items():
            self.cpp_info.components[target_lib].set_property("cmake_target_name", target_lib)
            self.cpp_info.components[target_lib].libs = [target_lib]
            self.cpp_info.components[target_lib].includedirs.append(os.path.join("include", "dcmtk"))
            self.cpp_info.components[target_lib].requires = requires

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[target_lib].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[target_lib].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        if self.settings.os == "Windows":
            self.cpp_info.components["ofstd"].system_libs.extend([
                "iphlpapi", "ws2_32", "netapi32", "wsock32"
            ])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ofstd"].system_libs.append("m")
            if self.options.with_multithreading:
                self.cpp_info.components["ofstd"].system_libs.append("pthread")

        dcmdictpath = os.path.join(self._dcm_datadictionary_path, "dcmtk", "dicom.dic")
        self.runenv_info.define_path("DCMDICTPATH", dcmdictpath)
        if self.options.with_applications:
            self.buildenv_info.define_path("DCMDICTPATH", dcmdictpath)

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "DCMTK"
        self.cpp_info.filenames["cmake_find_package_multi"] = "DCMTK"
        self.env_info.DCMDICTPATH = dcmdictpath
        if self.options.with_applications:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

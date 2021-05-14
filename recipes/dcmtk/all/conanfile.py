from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.33.0"


class DCMTKConan(ConanFile):
    name = "dcmtk"
    description = "DCMTK is a collection of libraries and applications implementing large parts the DICOM standard"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dicom.offis.de/dcmtk"
    license = "BSD-3-Clause"
    topics = "conan", "dcmtk", "dicom", "image"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_applications": [True, False],
        "with_multithreading": [True, False],
        "charset_conversion": [None, "libiconv", "icu"],
        "with_libxml2": [True, False],
        "with_zlib": [True, False],
        "with_openjpeg": [True, False, "deprecated"],
        "with_openssl": [True, False],
        "with_libpng": [True, False],
        "with_libsndfile": [True, False, "deprecated"],
        "with_libtiff": [True, False],
        "with_tcpwrappers": [True, False],
        "builtin_dictionary": [None, True, False],
        "builtin_private_tags": [True, False],
        "external_dictionary": [None, True, False],
        "wide_io": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_applications": False,
        "with_multithreading": True,
        "charset_conversion": "libiconv",
        "with_libxml2": True,
        "with_zlib": True,
        "with_openjpeg": "deprecated",
        "with_openssl": True,
        "with_libpng": True,
        "with_libsndfile": "deprecated",
        "with_libtiff": True,
        "with_tcpwrappers": False,
        "builtin_dictionary": None,
        "builtin_private_tags": False,
        "external_dictionary": None,
        "wide_io": False,
    }
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows":
            del self.options.with_tcpwrappers
        
        # Looking into source code, it appears that OpenJPEG and libsndfile are not used
        if self.options.with_openjpeg != "deprecated":
            self.output.warn("with_openjpeg option is deprecated, do not use anymore")
        if self.options.with_libsndfile != "deprecated":
            self.output.warn("with_libsndfile option is deprecated, do not use anymore")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        if self.options.charset_conversion == "libiconv":
            self.requires("libiconv/1.16")
        elif self.options.charset_conversion == "icu":
            self.requires("icu/68.2")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.10")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_openssl:
            # FIXME: Bump openssl. dcmtk build files have a logic to detect
            #        various openssl API but for some reason it fails with 1.1 API
            self.requires("openssl/1.0.2u")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_libtiff:
            self.requires("libtiff/4.2.0")
        if self.options.get_safe("with_tcpwrappers"):
            self.requires("tcp-wrappers/7.6")

    def package_id(self):
        del self.info.options.with_openjpeg
        del self.info.options.with_libsndfile

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        # DICOM Data Dictionaries are required
        self._cmake.definitions["CMAKE_INSTALL_DATADIR"] = self._dcm_datadictionary_path

        self._cmake.definitions["BUILD_APPS"] = self.options.with_applications
        self._cmake.definitions["DCMTK_WITH_ICONV"] = self.options.charset_conversion == "libiconv"
        if self.options.charset_conversion == "libiconv":
            self._cmake.definitions["WITH_LIBICONVINC"] = self.deps_cpp_info["libiconv"].rootpath
        self._cmake.definitions["DCMTK_WITH_ICU"] = self.options.charset_conversion == "icu"
        self._cmake.definitions["DCMTK_WITH_OPENJPEG"] = False
        self._cmake.definitions["DCMTK_WITH_OPENSSL"] = self.options.with_openssl
        if self.options.with_openssl:
            self._cmake.definitions["WITH_OPENSSLINC"] = self.deps_cpp_info["openssl"].rootpath
        self._cmake.definitions["DCMTK_WITH_PNG"] = self.options.with_libpng
        if self.options.with_libpng:
            self._cmake.definitions["WITH_LIBPNGINC"] = self.deps_cpp_info["libpng"].rootpath
        self._cmake.definitions["DCMTK_WITH_SNDFILE"] = False
        self._cmake.definitions["DCMTK_WITH_THREADS"] = self.options.with_multithreading
        self._cmake.definitions["DCMTK_WITH_TIFF"] = self.options.with_libtiff
        if self.options.with_libtiff:
            self._cmake.definitions["WITH_LIBTIFFINC"] = self.deps_cpp_info["libtiff"].rootpath
        if self.settings.os != "Windows":
            self._cmake.definitions["DCMTK_WITH_WRAP"] = self.options.with_tcpwrappers
        self._cmake.definitions["DCMTK_WITH_XML"] = self.options.with_libxml2
        if self.options.with_libxml2:
            self._cmake.definitions["WITH_LIBXMLINC"] = self.deps_cpp_info["libxml2"].rootpath
            self._cmake.definitions["WITH_LIBXML_SHARED"] = self.options["libxml2"].shared
        self._cmake.definitions["DCMTK_WITH_ZLIB"] = self.options.with_zlib
        if self.options.with_zlib:
            self._cmake.definitions["WITH_ZLIBINC"] = self.deps_cpp_info["zlib"].rootpath

        self._cmake.definitions["DCMTK_ENABLE_STL"] = True
        self._cmake.definitions["DCMTK_ENABLE_CXX11"] = True

        self._cmake.definitions["DCMTK_ENABLE_MANPAGE"] = False
        self._cmake.definitions["DCMTK_WITH_DOXYGEN"] = False

        self._cmake.definitions["DCMTK_ENABLE_PRIVATE_TAGS"] = self.options.builtin_private_tags
        if self.options.external_dictionary is not None:
            self._cmake.definitions["DCMTK_ENABLE_EXTERNAL_DICTIONARY"] = self.options.external_dictionary
        if self.options.builtin_dictionary is not None:
            self._cmake.definitions["DCMTK_ENABLE_BUILTIN_DICTIONARY"] = self.options.builtin_dictionary
        self._cmake.definitions["DCMTK_WIDE_CHAR_FILE_IO_FUNCTIONS"] = self.options.wide_io
        self._cmake.definitions["DCMTK_WIDE_CHAR_MAIN_FUNCTION"] = self.options.wide_io


        if self.settings.os == "Windows":
            self._cmake.definitions["DCMTK_OVERWRITE_WIN32_COMPILER_FLAGS"] = False

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["DCMTK_ICONV_FLAGS_ANALYZED"] = True
            self._cmake.definitions["DCMTK_COMPILE_WIN32_MULTITHREADED_DLL"] = "MD" in str(self.settings.compiler.runtime)

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {target: "DCMTK::{}".format(target) for target in self._dcmtk_components.keys()}
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

        charls = "dcmtkcharls" if tools.Version("3.6.6") <= self.version else "charls"

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
            "dcmjpls" : ["ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage", charls],
            charls    : ["ofstd", "oflog"],
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
        self.cpp_info.names["cmake_find_package"] = "DCMTK"
        self.cpp_info.names["cmake_find_package_multi"] = "DCMTK"

        def register_components(components):
            for target_lib, requires in components.items():
                self.cpp_info.components[target_lib].names["cmake_find_package"] = target_lib
                self.cpp_info.components[target_lib].names["cmake_find_package_multi"] = target_lib
                self.cpp_info.components[target_lib].builddirs.append(self._module_subfolder)
                self.cpp_info.components[target_lib].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[target_lib].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                self.cpp_info.components[target_lib].libs = [target_lib]
                self.cpp_info.components[target_lib].includedirs.append(os.path.join("include", "dcmtk"))
                self.cpp_info.components[target_lib].requires = requires

            if self.settings.os == "Windows":
                self.cpp_info.components["ofstd"].system_libs.extend([
                    "iphlpapi", "ws2_32", "netapi32", "wsock32"
                ])
            elif self.settings.os == "Linux":
                self.cpp_info.components["ofstd"].system_libs.append("m")
                if self.options.with_multithreading:
                    self.cpp_info.components["ofstd"].system_libs.append("pthread")

        register_components(self._dcmtk_components)

        dcmdictpath = os.path.join(self._dcm_datadictionary_path, "dcmtk", "dicom.dic")
        self.output.info("Settings DCMDICTPATH environment variable: {}".format(dcmdictpath))
        self.env_info.DCMDICTPATH = dcmdictpath

        if self.options.with_applications:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

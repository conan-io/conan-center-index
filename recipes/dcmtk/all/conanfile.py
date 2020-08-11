from conans import ConanFile, CMake, tools
import os


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
        "with_openjpeg": [True, False],
        "with_openssl": [True, False],
        "with_libpng": [True, False],
        "with_libsndfile": [True, False],
        "with_libtiff": [True, False],
        "with_tcpwrappers": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_applications": False,
        "with_multithreading": True,
        "charset_conversion": "libiconv",
        "with_libxml2": True,
        "with_zlib": True,
        "with_openjpeg": False,
        "with_openssl": True,
        "with_libpng": True,
        "with_libsndfile": False,
        "with_libtiff": True,
        "with_tcpwrappers": False,
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
        del self.options.with_openjpeg
        del self.options.with_libsndfile

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        if self.options.charset_conversion == "libiconv":
            self.requires("libiconv/1.16")
        elif self.options.charset_conversion == "icu":
            self.requires("icu/67.1")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.10")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.get_safe("with_openjpeg"):
            self.requires("openjpeg/2.3.1")
        if self.options.with_openssl:
            self.requires("openssl/1.0.2u")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.get_safe("with_libsndfile"):
            self.requires("libsndfile/1.0.28")
        if self.options.with_libtiff:
            self.requires("libtiff/4.1.0")
        if self.options.get_safe("with_tcpwrappers"):
            self.requires("tcp-wrappers/7.6")

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
        self._cmake.definitions["DCMTK_WITH_OPENJPEG"] = self.options.get_safe("with_openjpeg", False)
        if self.options.get_safe("with_openjpeg"):
            self._cmake.definitions["WITH_OPENJPEGINC"] = self.deps_cpp_info["openjpeg"].rootpath
        self._cmake.definitions["DCMTK_WITH_OPENSSL"] = self.options.with_openssl
        if self.options.with_openssl:
            self._cmake.definitions["WITH_OPENSSLINC"] = self.deps_cpp_info["openssl"].rootpath
        self._cmake.definitions["DCMTK_WITH_PNG"] = self.options.with_libpng
        if self.options.with_libpng:
            self._cmake.definitions["WITH_LIBPNGINC"] = self.deps_cpp_info["libpng"].rootpath
        self._cmake.definitions["DCMTK_WITH_SNDFILE"] = self.options.get_safe("with_libsndfile", False)
        if self.options.get_safe("with_libsndfile"):
            self._cmake.definitions["WITH_SNDFILEINC"] = self.deps_cpp_info["libsndfile"].rootpath
        self._cmake.definitions["DCMTK_WITH_THREADS"] = self.options.with_multithreading
        self._cmake.definitions["DCMTK_WITH_TIFF"] = self.options.with_libtiff
        if self.options.with_libtiff:
            self._cmake.definitions["WITH_LIBTIFFINC"] = self.deps_cpp_info["libtiff"].rootpath
        if self.settings.os != "Windows":
            self._cmake.definitions["DCMTK_WITH_WRAP"] = self.options.with_tcpwrappers
        self._cmake.definitions["DCMTK_WITH_XML"] = self.options.with_libxml2
        if self.options.with_libxml2:
            self._cmake.definitions["WITH_LIBXMLINC"] = self.deps_cpp_info["libxml2"].rootpath
        self._cmake.definitions["DCMTK_WITH_ZLIB"] = self.options.with_zlib
        if self.options.with_zlib:
            self._cmake.definitions["WITH_ZLIBINC"] = self.deps_cpp_info["zlib"].rootpath

        self._cmake.definitions["DCMTK_ENABLE_STL"] = True
        self._cmake.definitions["DCMTK_ENABLE_CXX11"] = True

        self._cmake.definitions["DCMTK_ENABLE_MANPAGE"] = False
        self._cmake.definitions["DCMTK_WITH_DOXYGEN"] = False

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

    @property
    def _dcm_datadictionary_path(self):
        return os.path.join(self.package_folder, "bin", "share")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "DCMTK"
        self.cpp_info.names["cmake_find_package_multi"] = "DCMTK"
        # TODO: imported targets shouldn't be namespaced
        includedir = os.path.join("include", "dcmtk")
        # ofstd
        self.cpp_info.components["ofstd"].includedirs.append(includedir)
        self.cpp_info.components["ofstd"].libs = ["ofstd"]
        if self.settings.os == "Windows":
            self.cpp_info.components["ofstd"].system_libs.extend(["iphlpapi", "ws2_32", "netapi32", "wsock32"])
        elif self.settings.os == "Linux":
            self.cpp_info.components["ofstd"].system_libs.append("m")
            if self.options.with_multithreading:
                self.cpp_info.components["ofstd"].system_libs.append("pthread")
        if self.options.charset_conversion == "libiconv":
            self.cpp_info.components["ofstd"].requires = ["libiconv::libiconv"]
        elif self.options.charset_conversion == "icu":
            self.cpp_info.components["ofstd"].requires = ["icu::icu"]
        # oflog
        self.cpp_info.components["oflog"].includedirs.append(includedir)
        self.cpp_info.components["oflog"].libs = ["oflog"]
        self.cpp_info.components["oflog"].requires = ["ofstd"]
        # dcmdata
        self.cpp_info.components["dcmdata"].includedirs.append(includedir)
        self.cpp_info.components["dcmdata"].libs = ["dcmdata"]
        self.cpp_info.components["dcmdata"].requires = ["ofstd", "oflog"]
        if self.options.with_zlib:
            self.cpp_info.components["dcmdata"].requires.append("zlib::zlib")
        # i2d
        self.cpp_info.components["i2d"].includedirs.append(includedir)
        self.cpp_info.components["i2d"].libs = ["i2d"]
        self.cpp_info.components["i2d"].requires = ["dcmdata"]
        # dcmimgle
        self.cpp_info.components["dcmimgle"].includedirs.append(includedir)
        self.cpp_info.components["dcmimgle"].libs = ["dcmimgle"]
        self.cpp_info.components["dcmimgle"].requires = ["ofstd", "oflog", "dcmdata"]
        # dcmimage
        self.cpp_info.components["dcmimage"].includedirs.append(includedir)
        self.cpp_info.components["dcmimage"].libs = ["dcmimage"]
        self.cpp_info.components["dcmimage"].requires = ["oflog", "dcmdata", "dcmimgle"]
        if self.options.with_libpng:
            self.cpp_info.components["dcmimage"].requires.append("libpng::libpng")
        if self.options.with_libtiff:
            self.cpp_info.components["dcmimage"].requires.append("libtiff::libtiff")
        # dcmjpeg
        self.cpp_info.components["dcmjpeg"].includedirs.append(includedir)
        self.cpp_info.components["dcmjpeg"].libs = ["dcmjpeg"]
        self.cpp_info.components["dcmjpeg"].requires = [
            "ofstd", "oflog", "dcmdata", "dcmimgle",
            "dcmimage", "ijg8", "ijg12", "ijg16"
        ]
        # ijg8
        self.cpp_info.components["ijg8"].includedirs.append(includedir)
        self.cpp_info.components["ijg8"].libs = ["ijg8"]
        # ijg12
        self.cpp_info.components["ijg12"].includedirs.append(includedir)
        self.cpp_info.components["ijg12"].libs = ["ijg12"]
        # ijg16
        self.cpp_info.components["ijg16"].includedirs.append(includedir)
        self.cpp_info.components["ijg16"].libs = ["ijg16"]
        # dcmjpls
        self.cpp_info.components["dcmjpls"].includedirs.append(includedir)
        self.cpp_info.components["dcmjpls"].libs = ["dcmjpls"]
        self.cpp_info.components["dcmjpls"].requires = ["ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage", "charls"]
        # charls
        self.cpp_info.components["charls"].includedirs.append(includedir)
        self.cpp_info.components["charls"].libs = ["charls"]
        self.cpp_info.components["charls"].requires = ["ofstd", "oflog"]
        # dcmtls
        self.cpp_info.components["dcmtls"].includedirs.append(includedir)
        self.cpp_info.components["dcmtls"].libs = ["dcmtls"]
        self.cpp_info.components["dcmtls"].requires = ["ofstd", "dcmdata", "dcmnet"]
        if self.options.with_openssl:
            self.cpp_info.components["dcmtls"].requires.append("openssl::openssl")
        # dcmnet
        self.cpp_info.components["dcmnet"].includedirs.append(includedir)
        self.cpp_info.components["dcmnet"].libs = ["dcmnet"]
        self.cpp_info.components["dcmnet"].requires = ["ofstd", "oflog", "dcmdata"]
        if self.options.get_safe("with_tcpwrappers"):
            self.cpp_info.components["dcmnet"].requires.append("tcp-wrappers::tcp-wrappers")
        # dcmsr
        self.cpp_info.components["dcmsr"].includedirs.append(includedir)
        self.cpp_info.components["dcmsr"].libs = ["dcmsr"]
        self.cpp_info.components["dcmsr"].requires = ["ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage"]
        if self.options.with_libxml2:
            self.cpp_info.components["dcmsr"].requires.append("libxml2::libxml2")
        # cmr
        self.cpp_info.components["cmr"].includedirs.append(includedir)
        self.cpp_info.components["cmr"].libs = ["cmr"]
        self.cpp_info.components["cmr"].requires = ["dcmsr"]
        # dcmdsig
        self.cpp_info.components["dcmdsig"].includedirs.append(includedir)
        self.cpp_info.components["dcmdsig"].libs = ["dcmdsig"]
        self.cpp_info.components["dcmdsig"].requires = ["ofstd", "dcmdata"]
        if self.options.with_openssl:
            self.cpp_info.components["dcmdsig"].requires.append("openssl::openssl")
        # dcmwlm
        self.cpp_info.components["dcmwlm"].includedirs.append(includedir)
        self.cpp_info.components["dcmwlm"].libs = ["dcmwlm"]
        self.cpp_info.components["dcmwlm"].requires = ["ofstd", "dcmdata", "dcmnet"]
        # dcmqrdb
        self.cpp_info.components["dcmqrdb"].includedirs.append(includedir)
        self.cpp_info.components["dcmqrdb"].libs = ["dcmqrdb"]
        self.cpp_info.components["dcmqrdb"].requires = ["ofstd", "dcmdata", "dcmnet"]
        # dcmpstat
        self.cpp_info.components["dcmpstat"].includedirs.append(includedir)
        self.cpp_info.components["dcmpstat"].libs = ["dcmpstat"]
        self.cpp_info.components["dcmpstat"].requires = [
            "ofstd", "oflog", "dcmdata", "dcmimgle", "dcmimage",
            "dcmnet", "dcmdsig", "dcmtls", "dcmsr", "dcmqrdb"
        ]
        if self.options.with_openssl:
            self.cpp_info.components["dcmpstat"].requires.append("openssl::openssl")
        # dcmrt
        self.cpp_info.components["dcmrt"].includedirs.append(includedir)
        self.cpp_info.components["dcmrt"].libs = ["dcmrt"]
        self.cpp_info.components["dcmrt"].requires = ["ofstd", "oflog", "dcmdata", "dcmimgle"]
        # dcmiod
        self.cpp_info.components["dcmiod"].includedirs.append(includedir)
        self.cpp_info.components["dcmiod"].libs = ["dcmiod"]
        self.cpp_info.components["dcmiod"].requires = ["dcmdata", "ofstd", "oflog"]
        # dcmfg
        self.cpp_info.components["dcmfg"].includedirs.append(includedir)
        self.cpp_info.components["dcmfg"].libs = ["dcmfg"]
        self.cpp_info.components["dcmfg"].requires = ["dcmiod", "dcmdata", "ofstd", "oflog"]
        # dcmseg
        self.cpp_info.components["dcmseg"].includedirs.append(includedir)
        self.cpp_info.components["dcmseg"].libs = ["dcmseg"]
        self.cpp_info.components["dcmseg"].requires = ["dcmfg", "dcmiod", "dcmdata", "ofstd", "oflog"]
        # dcmtract
        self.cpp_info.components["dcmtract"].includedirs.append(includedir)
        self.cpp_info.components["dcmtract"].libs = ["dcmtract"]
        self.cpp_info.components["dcmtract"].requires = ["dcmiod", "dcmdata", "ofstd", "oflog"]
        # dcmpmap
        self.cpp_info.components["dcmpmap"].includedirs.append(includedir)
        self.cpp_info.components["dcmpmap"].libs = ["dcmpmap"]
        self.cpp_info.components["dcmpmap"].requires = ["dcmfg", "dcmiod", "dcmdata", "ofstd", "oflog"]

        dcmdictpath = os.path.join(self._dcm_datadictionary_path, "dcmtk", "dicom.dic")
        self.output.info("Settings DCMDICTPATH environment variable: {}".format(dcmdictpath))
        self.env_info.DCMDICTPATH = dcmdictpath

        if self.options.with_applications:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

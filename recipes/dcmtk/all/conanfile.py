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
        "with_openjpeg": True,
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        if self.options.charset_conversion == "libiconv":
            self.requires("libiconv/1.16")
        elif self.options.charset_conversion == "icu":
            self.requires("icu/64.2")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.10")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.3.1")
        if self.options.with_openssl:
            self.requires("openssl/1.0.2u")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_libsndfile:
            self.requires("libsndfile/1.0.28")
        if self.options.with_libtiff:
            self.requires("libtiff/4.1.0")
        if self.options.with_tcpwrappers:
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
        self._cmake.definitions["DCMTK_WITH_OPENJPEG"] = self.options.with_openjpeg
        if self.options.with_openjpeg:
            self._cmake.definitions["WITH_OPENJPEGINC"] = self.deps_cpp_info["openjpeg"].rootpath
        self._cmake.definitions["DCMTK_WITH_OPENSSL"] = self.options.with_openssl
        if self.options.with_openssl:
            self._cmake.definitions["WITH_OPENSSLINC"] = self.deps_cpp_info["openssl"].rootpath
        self._cmake.definitions["DCMTK_WITH_PNG"] = self.options.with_libpng
        if self.options.with_libpng:
            self._cmake.definitions["WITH_LIBPNGINC"] = self.deps_cpp_info["libpng"].rootpath
        self._cmake.definitions["DCMTK_WITH_SNDFILE"] = self.options.with_libsndfile
        if self.options.with_libsndfile:
            self._cmake.definitions["WITH_SNDFILEINC"] = self.deps_cpp_info["libsndfile"].rootpath
        self._cmake.definitions["DCMTK_WITH_THREADS"] = self.options.with_multithreading
        self._cmake.definitions["DCMTK_WITH_TIFF"] = self.options.with_libtiff
        if self.options.with_libtiff:
            self._cmake.definitions["WITH_LIBTIFFINC"] = self.deps_cpp_info["libtiff"].rootpath
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
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "dcmtk"))
        self.cpp_info.names["cmake_find_package"] = "DCMTK"
        self.cpp_info.names["cmake_find_package_multi"] = "DCMTK"

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["iphlpapi", "ws2_32", "netapi32", "wsock32"])

        dcmdictpath = os.path.join(self._dcm_datadictionary_path, "dcmtk", "dicom.dic")
        self.output.info("Settings DCMDICTPATH environment variable: {}".format(dcmdictpath))
        self.env_info.DCMDICTPATH = dcmdictpath

        if self.options.with_applications:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

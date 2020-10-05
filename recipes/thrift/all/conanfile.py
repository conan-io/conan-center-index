from conans import tools, CMake, ConanFile
from conans.errors import ConanInvalidConfiguration
import os


class ConanFileDefault(ConanFile):
    name = "thrift"
    description = "Thrift is an associated code generation mechanism for RPC"
    topics = ("conan", "thrift", "serialization", "rpc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/thrift"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*.diff"]
    generators = "cmake", "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_libevent": [True, False],
        "with_openssl": [True, False],
        "with_boost_functional": [True, False],
        "with_boost_smart_ptr": [True, False],
        "with_boost_static": [True, False],
        "with_boostthreads": [True, False],
        "with_stdthreads": [True, False],
        "with_c_glib": [True, False],
        "with_cpp": [True, False],
        "with_java": [True, False],
        "with_python": [True, False],
        "with_qt": [True, False],
        "with_haskell": [True, False],
        "with_plugin": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_libevent": True,
        "with_openssl": True,
        "with_boost_functional": False,
        "with_boost_smart_ptr": False,
        "with_boost_static": False,
        "with_boostthreads": False,
        "with_stdthreads": True,
        "with_c_glib": False,
        "with_cpp": True,
        "with_java": False,
        "with_python": False,
        "with_qt": False,
        "with_haskell": False,
        "with_plugin": False
    }
    short_paths = True

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
        extracted_dir = "thrift-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("winflexbison/2.5.22")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.5.3")

    def requirements(self):
        self.requires("boost/1.74.0")

        if self.options.with_qt:
            # FIXME: missing qt recipe
            raise ConanInvalidConfiguration("qt is not (yet) available on cci")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1h")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_libevent:
            self.requires("libevent/2.1.11")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        for option, value in self.options.items():
            self._cmake.definitions[option.upper()] = value

        # Make thrift use correct thread lib (see repo/build/cmake/config.h.in)
        self._cmake.definitions["USE_STD_THREAD"] = self.options.with_stdthreads
        self._cmake.definitions["USE_BOOST_THREAD"] = self.options.with_boostthreads
        self._cmake.definitions["WITH_SHARED_LIB"] = self.options.shared
        self._cmake.definitions["WITH_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["BOOST_ROOT"] = self.deps_cpp_info["boost"].rootpath
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_COMPILER"] = True
        self._cmake.definitions["BUILD_LIBRARIES"] = True
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TUTORIALS"] = False

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["WITH_MT"] = "MT" in str(self.settings.compiler.runtime)

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
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)
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

    def package_info(self):
        libsuffix = "{}{}".format(
            str(self.settings.compiler.runtime).lower()[:2] if self.settings.compiler == "Visual Studio" else "",
            "d" if self.settings.build_type == "Debug" else ""
        )

        self.cpp_info.filenames["cmake_find_package"] = "Thrift"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Thrift"
        self.cpp_info.names["cmake_find_package"] = "thrift"
        self.cpp_info.names["cmake_find_package_multi"] = "thrift"

        self.cpp_info.components["libthrift"].libs = ["thrift" + libsuffix]
        self.cpp_info.components["libthrift"].names["cmake_find_package"] = "thrift"
        self.cpp_info.components["libthrift"].names["cmake_find_package_multi"] = "thrift"
        self.cpp_info.components["libthrift"].names["pkg_config"] = "thrift"
        if self.settings.os == "Windows":
            self.cpp_info.components["libthrift"].defines.append("NOMINMAX")
        elif self.settings.os == "Linux":
            self.cpp_info.components["libthrift"].system_libs.extend(["m", "pthread"])
        self.cpp_info.components["libthrift"].requires.append("boost::boost")
        if self.options.with_openssl:
            self.cpp_info.components["libthrift"].requires.append("openssl::openssl")
        if self.options.with_libevent:
            self.cpp_info.components["libthrift"].requires.append("libevent::libevent")

        # FIXME: this generates thrift::thriftz, but should be thriftz::thriftz
        if self.options.with_zlib:
            self.cpp_info.components["libthrift_z"].libs = ["thriftz" + libsuffix]
            self.cpp_info.components["libthrift_z"].requires = ["libthrift", "zlib::zlib"]
            self.cpp_info.components["libthrift_z"].names["cmake_find_package"] = "thriftz"
            self.cpp_info.components["libthrift_z"].names["cmake_find_package_multi"] = "thriftz"
            self.cpp_info.components["libthrift_z"].names["pkg_config"] = "thrift-z"

        # FIXME: this generates thrift::thriftnb, but should be thriftnb::thriftnb
        self.cpp_info.components["libthrift_nb"].libs = ["thriftnb" + libsuffix]
        self.cpp_info.components["libthrift_nb"].requires = ["libthrift"]
        self.cpp_info.components["libthrift_nb"].names["cmake_find_package"] = "thriftnb"
        self.cpp_info.components["libthrift_nb"].names["cmake_find_package_multi"] = "thriftnb"
        self.cpp_info.components["libthrift_nb"].names["pkg_config"] = "thrift-nb"

        # FIXME: this generates thrift::thriftqt5, but should be thriftqt5::thriftqt5
        if self.options.with_qt:
            self.cpp_info.components["libthrift_qt5"].libs = ["thriftqt5" + libsuffix]
            self.cpp_info.components["libthrift_qt5"].requires = ["libthrift", "qt::core"]
            self.cpp_info.components["libthrift_qt5"].names["cmake_find_package"] = "thriftqt5"
            self.cpp_info.components["libthrift_qt5"].names["cmake_find_package_multi"] = "thriftqt5"
            self.cpp_info.components["libthrift_qt5"].names["pkg_config"] = "thrift-qt5"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

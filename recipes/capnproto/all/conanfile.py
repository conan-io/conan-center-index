from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import glob
import os
import textwrap

required_conan_version = ">=1.33.0"


class CapnprotoConan(ConanFile):
    name = "capnproto"
    description = "Cap'n Proto serialization/RPC system."
    license = "MIT"
    topics = ("conan", "capnproto", "serialization", "rpc")
    homepage = "https://capnproto.org"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ("CMakeLists.txt", "patches/**")
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_zlib": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_zlib": True
    }

    _cmake = None
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "0.8.0":
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("Cap'n Proto requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Cap'n Proto requires C++14, which your compiler does not support.")
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("Cap'n Proto doesn't support shared libraries for Visual Studio")
        if self.settings.os == "Windows" and tools.Version(self.version) < "0.8.0" and self.options.with_openssl:
            raise ConanInvalidConfiguration("Cap'n Proto doesn't support OpenSSL on Windows pre 0.8.0")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1k")
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.11")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["EXTERNAL_CAPNP"] = False
        self._cmake.definitions["CAPNP_LITE"] = False
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        args = [
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
            "--with-openssl" if self.options.with_openssl else "--without-openssl",
            "--enable-reflection"
        ]
        if tools.Version(self.version) >= "0.8.0":
            args.append("--with-zlib" if self.options.with_zlib else "--without-zlib")

        self._autotools = AutoToolsBuildEnvironment(self)

        # Fix rpath on macOS
        configure_dir = os.path.join(self._source_subfolder, "c++")
        configure_path = os.path.join(configure_dir, "configure")
        if self.settings.os == "Macos":
            tools.replace_in_file(configure_path, r"-install_name \$rpath/", "-install_name @rpath/")
            self._autotools.link_flags.append("-Wl,-rpath,@loader_path/../lib")

        self._autotools.configure(args=args, configure_dir=configure_dir)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            with tools.chdir(os.path.join(self._source_subfolder, "c++")):
                self.run("{} --install --verbose -Wall".format(tools.get_env("AUTORECONF")))
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _cmake_folder(self):
        return os.path.join("lib", "cmake", "CapnProto")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for cmake_file in glob.glob(os.path.join(self.package_folder, self._cmake_folder, "*")):
            if os.path.basename(cmake_file) != "CapnProtoMacros.cmake":
                os.remove(cmake_file)
        # inject mandatory variables so that CAPNP_GENERATE_CPP function can
        # work in a robust way (build from source or from pre build package)
        find_execs = textwrap.dedent("""\
            if(CMAKE_CROSSCOMPILING)
                find_program(CAPNP_EXECUTABLE capnp PATHS ENV PATH NO_DEFAULT_PATH)
                find_program(CAPNPC_CXX_EXECUTABLE capnpc-c++ PATHS ENV PATH NO_DEFAULT_PATH)
            endif()
            if(NOT CAPNP_EXECUTABLE)
                set(CAPNP_EXECUTABLE "${CMAKE_CURRENT_LIST_DIR}/../../../bin/capnp${CMAKE_EXECUTABLE_SUFFIX}")
            endif()
            if(NOT CAPNPC_CXX_EXECUTABLE)
                set(CAPNPC_CXX_EXECUTABLE "${CMAKE_CURRENT_LIST_DIR}/../../../bin/capnpc-c++${CMAKE_EXECUTABLE_SUFFIX}")
            endif()
            set(CAPNP_INCLUDE_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/../../../include")
            function(CAPNP_GENERATE_CPP SOURCES HEADERS)
        """)
        tools.replace_in_file(os.path.join(self.package_folder, self._cmake_folder, "CapnProtoMacros.cmake"),
                              "function(CAPNP_GENERATE_CPP SOURCES HEADERS)",
                              find_execs)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CapnProto"
        self.cpp_info.names["cmake_find_package_multi"] = "CapnProto"

        components = [
            {"name": "capnp", "requires": ["kj"]},
            {"name": "capnp-json", "requires": ["capnp", "kj"]},
            {"name": "capnp-rpc", "requires": ["capnp", "kj", "kj-async"]},
            {"name": "capnpc", "requires": ["capnp", "kj"]},
            {"name": "kj", "requires": []},
            {"name": "kj-async", "requires": ["kj"]},
            {"name": "kj-http", "requires": ["kj", "kj-async"]},
            {"name": "kj-test", "requires": ["kj"]},
        ]
        if self.options.get_safe("with_zlib"):
            components.append({"name": "kj-gzip", "requires": ["kj", "kj-async", "zlib::zlib"]})
        if self.options.with_openssl:
            components.append({"name": "kj-tls", "requires": ["kj", "kj-async", "openssl::openssl"]})

        for component in components:
            self._register_component(component)

        if self.settings.os == "Linux":
            self.cpp_info.components["capnpc"].system_libs = ["pthread"]
            self.cpp_info.components["kj"].system_libs = ["pthread"]
            self.cpp_info.components["kj-async"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["kj-async"].system_libs = ["ws2_32"]
        self.cpp_info.components["kj"].builddirs.append(self._cmake_folder)
        self.cpp_info.components["kj"].build_modules = [os.path.join(self._cmake_folder, "CapnProtoMacros.cmake")]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

    def _register_component(self, component):
        name = component["name"]
        self.cpp_info.components[name].names["cmake_find_package"] = name
        self.cpp_info.components[name].names["cmake_find_package_multi"] = name
        self.cpp_info.components[name].names["pkg_config"] = name
        self.cpp_info.components[name].libs = [name]
        self.cpp_info.components[name].requires = component["requires"]

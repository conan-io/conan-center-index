from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import glob
import os
import textwrap
import functools

required_conan_version = ">=1.43.0"


class CapnprotoConan(ConanFile):
    name = "capnproto"
    description = "Cap'n Proto serialization/RPC system."
    license = "MIT"
    topics = ("capnproto", "serialization", "rpc")
    homepage = "https://capnproto.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_zlib": True,
    }

    generators = "cmake", "cmake_find_package"

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

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "0.8.0":
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1o")
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("Cap'n Proto requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Cap'n Proto requires C++14, which your compiler does not support.")
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("Cap'n Proto doesn't support shared libraries for Visual Studio")
        if self.settings.os == "Windows" and tools.Version(self.version) < "0.8.0" and self.options.with_openssl:
            raise ConanInvalidConfiguration("Cap'n Proto doesn't support OpenSSL on Windows pre 0.8.0")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["EXTERNAL_CAPNP"] = False
        cmake.definitions["CAPNP_LITE"] = False
        cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    @functools.lru_cache(1)
    def _configure_autotools(self):
        args = [
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
            "--with-openssl" if self.options.with_openssl else "--without-openssl",
            "--enable-reflection",
        ]
        if tools.Version(self.version) >= "0.8.0":
            args.append("--with-zlib" if self.options.with_zlib else "--without-zlib")
        autotools = AutoToolsBuildEnvironment(self)
        # Fix rpath on macOS
        if self.settings.os == "Macos":
            autotools.link_flags.append("-Wl,-rpath,@loader_path/../lib")
        autotools.configure(args=args)
        return autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            with tools.chdir(os.path.join(self._source_subfolder, "c++")):
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")))
                # relocatable shared libs on macOS
                tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name @rpath/")
                # avoid SIP issues on macOS when dependencies are shared
                if tools.is_apple_os(self.settings.os):
                    libpaths = ":".join(self.deps_cpp_info.lib_paths)
                    tools.replace_in_file(
                        "configure",
                        "#! /bin/sh\n",
                        "#! /bin/sh\nexport DYLD_LIBRARY_PATH={}:$DYLD_LIBRARY_PATH\n".format(libpaths),
                    )
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
            with tools.chdir(os.path.join(self._source_subfolder, "c++")):
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
        self.cpp_info.set_property("cmake_file_name", "CapnProto")
        capnprotomacros = os.path.join(self._cmake_folder, "CapnProtoMacros.cmake")
        self.cpp_info.set_property("cmake_build_modules", [capnprotomacros])

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
        if tools.Version(self.version) >= "0.9.0":
            components.append({
                "name": "capnp-websocket",
                "requires": ["capnp", "capnp-rpc", "kj-http", "kj-async", "kj"],
            })

        for component in components:
            self._register_component(component)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["capnpc"].system_libs = ["pthread"]
            self.cpp_info.components["kj"].system_libs = ["pthread"]
            self.cpp_info.components["kj-async"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["kj-async"].system_libs = ["ws2_32"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CapnProto"
        self.cpp_info.names["cmake_find_package_multi"] = "CapnProto"
        self.cpp_info.components["kj"].build_modules = [capnprotomacros]

    def _register_component(self, component):
        name = component["name"]
        self.cpp_info.components[name].set_property("cmake_target_name", "CapnProto::{}".format(name))
        self.cpp_info.components[name].builddirs.append(self._cmake_folder)
        self.cpp_info.components[name].set_property("pkg_config_name", name)
        self.cpp_info.components[name].libs = [name]
        self.cpp_info.components[name].requires = component["requires"]

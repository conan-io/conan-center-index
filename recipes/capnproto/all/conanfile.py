from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import glob
import os
import textwrap

required_conan_version = ">=1.54.0"


class CapnprotoConan(ConanFile):
    name = "capnproto"
    description = "Cap'n Proto serialization/RPC system."
    license = "MIT"
    topics = ("serialization", "rpc")
    homepage = "https://capnproto.org"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
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

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.8.0":
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/3.1.0")
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.13")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support shared libraries for Visual Studio")
        if self.settings.os == "Windows" and Version(self.version) < "0.8.0" and self.options.with_openssl:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support OpenSSL on Windows pre 0.8.0")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("libtool/2.4.7")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.variables["BUILD_TESTING"] = False
            tc.variables["EXTERNAL_CAPNP"] = False
            tc.variables["CAPNP_LITE"] = False
            tc.variables["WITH_OPENSSL"] = self.options.with_openssl
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")
            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--with-openssl={yes_no(self.options.with_openssl)}",
                "--enable-reflection",
            ])
            if Version(self.version) >= "0.8.0":
                tc.configure_args.append(f"--with-zlib={yes_no(self.options.with_zlib)}")
            # Fix rpath on macOS
            if self.settings.os == "Macos":
                tc.extra_ldflags.append("-Wl,-rpath,@loader_path/../lib")
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            with chdir(self, os.path.join(self.source_folder, "c++")):
                autotools = Autotools(self)
                # TODO: replace by a call to autootols.autoreconf() in c++ folder once https://github.com/conan-io/conan/issues/12103 implemented
                self.run("autoreconf --force --install")
                autotools.configure(build_script_folder=os.path.join(self.source_folder, "c++"))
                autotools.make()

    @property
    def _cmake_folder(self):
        return os.path.join("lib", "cmake", "CapnProto")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            with chdir(self, os.path.join(self.source_folder, "c++")):
                autotools = Autotools(self)
                autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
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
        replace_in_file(self, os.path.join(self.package_folder, self._cmake_folder, "CapnProtoMacros.cmake"),
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
        if Version(self.version) >= "0.9.0":
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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CapnProto"
        self.cpp_info.names["cmake_find_package_multi"] = "CapnProto"
        self.cpp_info.components["kj"].build_modules = [capnprotomacros]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var with: {bin_path}")
        self.env_info.PATH.append(bin_path)

    def _register_component(self, component):
        name = component["name"]
        self.cpp_info.components[name].set_property("cmake_target_name", f"CapnProto::{name}")
        self.cpp_info.components[name].builddirs.append(self._cmake_folder)
        self.cpp_info.components[name].set_property("pkg_config_name", name)
        self.cpp_info.components[name].libs = [name]
        self.cpp_info.components[name].requires = component["requires"]

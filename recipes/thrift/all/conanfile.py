import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class ThriftConan(ConanFile):
    name = "thrift"
    description = "Thrift is an associated code generation mechanism for RPC"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/thrift"
    topics = ("thrift", "serialization", "rpc")
    package_type = "library"
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
    implements = ["auto_shared_fpic"]
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.85.0", transitive_headers=True)
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_qt5:
            self.requires("qt/[~5.15]")

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")
        if self.options.with_qt5:
            self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        # No static code analysis (seems to trigger CMake warnings due to weird custom Find module file)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "include(StaticCodeAnalysis)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        for option, value in self.options.items():
            if option.startswith("with_"):
                tc.variables[option.upper()] = value
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_COMPILER"] = True
        tc.variables["BUILD_LIBRARIES"] = True
        tc.variables["BUILD_TUTORIALS"] = False
        tc.variables["WITH_QT5"] = self.options.with_qt5
        if is_msvc(self):
            tc.variables["WITH_MT"] = is_msvc_static_runtime(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0074"] = "NEW"
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Copy generated headers from build tree
        copy(self, "*.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include"), keep_path=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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
        self.cpp_info.components["libthrift"].libs = [f"thrift{libsuffix}"]
        if self.settings.os == "Windows":
            if Version(self.version) >= "0.15.0":
                self.cpp_info.components["libthrift"].system_libs.append("shlwapi")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libthrift"].system_libs.extend(["m", "pthread"])
        self.cpp_info.components["libthrift"].requires.append("boost::headers")
        if self.options.with_openssl:
            self.cpp_info.components["libthrift"].requires.append("openssl::openssl")

        if self.options.with_zlib:
            self.cpp_info.components["libthrift_z"].set_property("cmake_target_name", "thriftz::thriftz")
            self.cpp_info.components["libthrift_z"].set_property("pkg_config_name", "thrift-z")
            self.cpp_info.components["libthrift_z"].libs = [f"thriftz{libsuffix}"]
            self.cpp_info.components["libthrift_z"].requires = ["libthrift", "zlib::zlib"]


        if self.options.with_libevent:
            self.cpp_info.components["libthrift_nb"].set_property("cmake_target_name", "thriftnb::thriftnb")
            self.cpp_info.components["libthrift_nb"].set_property("pkg_config_name", "thrift-nb")
            self.cpp_info.components["libthrift_nb"].libs = [f"thriftnb{libsuffix}"]
            self.cpp_info.components["libthrift_nb"].requires = ["libthrift", "libevent::libevent"]

        if self.options.with_qt5:
            self.cpp_info.components["libthrift_qt5"].set_property("cmake_target_name", "thriftqt5::thriftqt5")
            self.cpp_info.components["libthrift_qt5"].set_property("pkg_config_name", "thrift-qt5")
            self.cpp_info.components["libthrift_qt5"].libs = [f"thriftqt5{libsuffix}"]
            self.cpp_info.components["libthrift_qt5"].requires = ["libthrift", "qt::qtCore"]

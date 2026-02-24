from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


class MongoCDriverConan(ConanFile):
    name = "mongo-c-driver"
    description = "A Cross Platform MongoDB Client Library for C"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mongoc.org/"
    topics = ("libbson", "libmongoc", "mongo", "mongodb", "database", "db")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [False, "darwin", "windows", "openssl", "libressl"],
        "with_sasl": [False, "sspi", "cyrus"],
        "with_snappy": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_icu": [True, False],
        "srv": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl",
        "with_sasl": False,
        "with_snappy": True,
        "with_zlib": True,
        "with_zstd": True,
        "with_icu": True,
        "srv": True,
    }

    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.with_sasl = "sspi"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.with_ssl == "libressl":
            self.requires("libressl/3.5.3")
        if self.options.with_sasl == "cyrus":
            self.requires("cyrus-sasl/2.1.28")
        if self.options.with_snappy:
            self.requires("snappy/1.1.10")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_zstd:
            self.requires("zstd/[^1.5]")
        if self.options.with_icu:
            self.requires("icu/74.2")

    def validate(self):
        if self.options.with_ssl == "darwin" and not is_apple_os(self):
            raise ConanInvalidConfiguration("with_ssl=darwin only allowed on Apple os family")
        if self.options.with_ssl == "windows" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_ssl=windows only allowed on Windows")
        if self.options.with_sasl == "sspi" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_sasl=sspi only allowed on Windows")

    def build_requirements(self):
        if self.options.with_ssl == "libressl" or self.options.with_zstd:
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _ssl_cmake_value(self):
        return {
            "darwin": "DARWIN",
            "windows": "WINDOWS",
            "openssl": "OPENSSL",
            "libressl": "LIBRESSL",
        }.get(str(self.options.with_ssl), "OFF")

    @property
    def _sasl_cmake_value(self):
        return {
            "sspi": "SSPI",
            "cyrus": "CYRUS",
        }.get(str(self.options.with_sasl), "OFF")

    def generate(self):
        tc = CMakeToolchain(self)
        # All these variables are option() declared before project() in upstream CMakeLists
        # therefore it defeats conan_toolchain variables, but it works fine with cache_variables
        tc.cache_variables["ENABLE_SSL"] = self._ssl_cmake_value
        tc.cache_variables["ENABLE_SASL"] = self._sasl_cmake_value
        tc.cache_variables["ENABLE_SHARED"] = self.options.shared
        tc.cache_variables["ENABLE_STATIC"] = not self.options.shared
        tc.cache_variables["ENABLE_TESTS"] = "OFF"
        tc.cache_variables["ENABLE_EXAMPLES"] = "OFF"
        tc.cache_variables["ENABLE_SRV"] = self.options.srv
        tc.cache_variables["ENABLE_MAINTAINER_FLAGS"] = "OFF"
        tc.cache_variables["ENABLE_AUTOMATIC_INIT_AND_CLEANUP"] = "ON"
        tc.cache_variables["ENABLE_CRYPTO_SYSTEM_PROFILE"] = "OFF"
        tc.cache_variables["ENABLE_TRACING"] = "OFF"
        tc.cache_variables["ENABLE_COVERAGE"] = "OFF"
        tc.cache_variables["ENABLE_SHM_COUNTERS"] = "OFF"
        tc.cache_variables["ENABLE_MONGOC"] = "ON"
        tc.cache_variables["ENABLE_BSON"] = "ON"
        tc.cache_variables["ENABLE_SNAPPY"] = self.options.with_snappy
        tc.cache_variables["ENABLE_ZLIB"] = "SYSTEM" if self.options.with_zlib else "OFF"
        tc.cache_variables["ENABLE_ZSTD"] = self.options.with_zstd
        tc.cache_variables["ENABLE_MAN_PAGES"] = "OFF"
        tc.cache_variables["ENABLE_HTML_DOCS"] = "OFF"
        tc.cache_variables["ENABLE_EXTRA_ALIGNMENT"] = "ON"
        tc.cache_variables["ENABLE_RDTSCP"] = "OFF"
        tc.cache_variables["ENABLE_APPLE_FRAMEWORK"] = "OFF"
        tc.cache_variables["ENABLE_ICU"] = self.options.with_icu
        tc.cache_variables["ENABLE_UNINSTALL"] = "OFF"
        tc.cache_variables["ENABLE_CLIENT_SIDE_ENCRYPTION"] = "OFF"  # libmongocrypt recipe not yet in CCI
        tc.cache_variables["ENABLE_MONGODB_AWS_AUTH"] = "AUTO"
        tc.cache_variables["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        # Avoid to install vc runtime stuff
        tc.variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = "TRUE"
        if self.options.with_ssl == "openssl":
            tc.variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        tc.variables["MONGO_USE_CCACHE"] = False
        if is_msvc(self):
            # Should be added because of
            # https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-initonceexecuteonce
            tc.preprocessor_definitions["_WIN32_WINNT"] = "0x0600"
        tc.cache_variables["BUILD_VERSION"] = self.version
        # Skip some fragile checks
        # https://github.com/mongodb/mongo-c-driver/blob/1.25.3/src/libmongoc/CMakeLists.txt#L266-L276
        tc.variables["HAVE_ASN1_STRING_GET0_DATA"] = True  # Requires OpenSSL 1.1.0+
        # https://github.com/mongodb/mongo-c-driver/blob/1.25.3/src/libmongoc/CMakeLists.txt#L366-L375
        tc.variables["SASL2_HAVE_SASL_CLIENT_DONE"] = True # Requires Cyrus-SASL 2.1.23+
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        if self.options.with_ssl == "libressl" or self.options.with_zstd:
            deps = PkgConfigDeps(self)
            deps.generate()
            env = VirtualBuildEnv(self)
            env.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        libmongoc_cmake = os.path.join(self.source_folder, "src", "libmongoc", "CMakeLists.txt")
        replace_in_file(self, libmongoc_cmake,
                        "include (FindSnappy)\nif (SNAPPY_INCLUDE_DIRS)",
                        'if(ENABLE_SNAPPY MATCHES "ON")\n  find_package(Snappy REQUIRED)')
        replace_in_file(self, libmongoc_cmake, "SNAPPY_LIBRARIES", "Snappy_LIBRARIES")
        replace_in_file(self, libmongoc_cmake, "SNAPPY_INCLUDE_DIRS", "Snappy_INCLUDE_DIRS")
        if Version(self.version) < "1.25":
            replace_in_file(self, libmongoc_cmake, "set (SSL_LIBRARIES -ltls -lcrypto)", "")
        # cleanup rpath
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "set (CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "THIRD_PARTY_NOTICES", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: two CMake module/config files should be generated (mongoc-1.0-config.cmake and bson-1.0-config.cmake),
        # but it can't be modeled right now.
        version_major = str(Version(self.version).major)
        is_major_version_1 = version_major == "1"

        cmake_name = "mongoc-1.0" if is_major_version_1 else "mongoc"

        self.cpp_info.set_property("cmake_file_name", cmake_name)

        lib_type = "shared" if self.options.shared else "static"

        self.cpp_info.set_property("cmake_target_name", f"mongo::mongoc_{lib_type}")

        for component in ["mongoc", "bson"]:
            target = f"{component}_{lib_type}"

            # mongo-c-driver 2.x makes changes to CMake target names. Use aliases for backward compatibility.
            # https://github.com/mongodb/mongo-c-driver/pull/1955
            self.cpp_info.components[component].set_property("cmake_target_name", f"mongo::{target}")
            self.cpp_info.components[component].set_property("cmake_target_aliases", [f"{component}::{lib_type}"])

            lib_type_suffix = '' if self.options.shared else '-static'

            pkg_config_name = f"lib{component}{lib_type_suffix}-1.0" if is_major_version_1 else f"{component}{version_major}{lib_type_suffix}"
            self.cpp_info.components[component].set_property("pkg_config_name", pkg_config_name)

            include_subdir = f"lib{component}-1.0" if is_major_version_1 else f"{component}-{self.version}"
            self.cpp_info.components[component].includedirs = [os.path.join("include", include_subdir)]

            lib = f"{component}{lib_type_suffix}-1.0" if is_major_version_1 else f"{component}{version_major}"
            self.cpp_info.components[component].libs = [lib]

        # mongoc
        if not self.options.shared:
            self.cpp_info.components["mongoc"].defines = ["MONGOC_STATIC"]
        self.cpp_info.components["mongoc"].requires = ["bson"]
        if self.settings.os == "Windows":
            self.cpp_info.components["mongoc"].system_libs.append("ws2_32")
        if self.options.with_ssl == "darwin":
            self.cpp_info.components["mongoc"].frameworks.extend(["CoreFoundation", "Security"])
        elif self.options.with_ssl == "windows":
            self.cpp_info.components["mongoc"].system_libs.extend(["secur32", "crypt32", "bcrypt"])
        elif self.options.with_ssl == "openssl":
            self.cpp_info.components["mongoc"].requires.append("openssl::openssl")
        elif self.options.with_ssl == "libressl":
            self.cpp_info.components["mongoc"].requires.append("libressl::libressl")
        if self.options.with_sasl == "sspi":
            self.cpp_info.components["mongoc"].system_libs.extend(["secur32", "crypt32", "shlwapi"])
        elif self.options.with_sasl == "cyrus":
            self.cpp_info.components["mongoc"].requires.append("cyrus-sasl::cyrus-sasl")
        if self.options.with_snappy:
            self.cpp_info.components["mongoc"].requires.append("snappy::snappy")
        if self.options.with_zlib:
            self.cpp_info.components["mongoc"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["mongoc"].requires.append("zstd::zstd")
        if self.options.with_icu:
            self.cpp_info.components["mongoc"].requires.append("icu::icu")
        if self.options.srv:
            self.cpp_info.components["mongoc"].system_libs.append("dnsapi" if self.settings.os == "Windows" else "resolv")

        # bson
        if not self.options.shared:
            self.cpp_info.components["bson"].defines = ["BSON_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["bson"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["bson"].system_libs = ["ws2_32"]

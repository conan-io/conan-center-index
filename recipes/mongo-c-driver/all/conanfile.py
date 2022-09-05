from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.3"


class MongoCDriverConan(ConanFile):
    name = "mongo-c-driver"
    description = "A Cross Platform MongoDB Client Library for C"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mongoc.org/"
    topics = ("libbson", "libmongoc", "mongo", "mongodb", "database", "db")

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.with_sasl = "sspi"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.with_ssl == "libressl":
            self.requires("libressl/3.5.3")
        if self.options.with_sasl == "cyrus":
            self.requires("cyrus-sasl/2.1.27")
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.with_icu:
            self.requires("icu/71.1")

    def validate(self):
        if self.info.options.with_ssl == "darwin" and not is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("with_ssl=darwin only allowed on Apple os family")
        if self.info.options.with_ssl == "windows" and self.info.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_ssl=windows only allowed on Windows")
        if self.info.options.with_sasl == "sspi" and self.info.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_sasl=sspi only allowed on Windows")

    def build_requirements(self):
        if self.options.with_ssl == "libressl" or self.options.with_zstd:
            self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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
        tc.cache_variables["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
        tc.cache_variables["ENABLE_TESTS"] = "OFF"
        tc.cache_variables["ENABLE_EXAMPLES"] = "OFF"
        tc.cache_variables["ENABLE_SRV"] = "ON" if self.options.srv else "OFF"
        tc.cache_variables["ENABLE_MAINTAINER_FLAGS"] = "OFF"
        tc.cache_variables["ENABLE_AUTOMATIC_INIT_AND_CLEANUP"] = "ON"
        tc.cache_variables["ENABLE_CRYPTO_SYSTEM_PROFILE"] = "OFF"
        tc.cache_variables["ENABLE_TRACING"] = "OFF"
        tc.cache_variables["ENABLE_COVERAGE"] = "OFF"
        tc.cache_variables["ENABLE_SHM_COUNTERS"] = "OFF"
        tc.cache_variables["ENABLE_MONGOC"] = "ON"
        tc.cache_variables["ENABLE_BSON"] = "ON"
        tc.cache_variables["ENABLE_SNAPPY"] = "ON" if self.options.with_snappy else "OFF"
        tc.cache_variables["ENABLE_ZLIB"] = "SYSTEM" if self.options.with_zlib else "OFF"
        tc.cache_variables["ENABLE_ZSTD"] = "ON" if self.options.with_zstd else "OFF"
        tc.cache_variables["ENABLE_MAN_PAGES"] = "OFF"
        tc.cache_variables["ENABLE_HTML_DOCS"] = "OFF"
        tc.cache_variables["ENABLE_EXTRA_ALIGNMENT"] = "ON"
        tc.cache_variables["ENABLE_RDTSCP"] = "OFF"
        tc.cache_variables["ENABLE_APPLE_FRAMEWORK"] = "OFF"
        tc.cache_variables["ENABLE_ICU"] = "ON" if self.options.with_icu else "OFF"
        tc.cache_variables["ENABLE_UNINSTALL"] = "OFF"
        tc.cache_variables["ENABLE_CLIENT_SIDE_ENCRYPTION"] = "OFF"  # libmongocrypt recipe not yet in CCI
        tc.cache_variables["ENABLE_MONGODB_AWS_AUTH"] = "AUTO"
        tc.cache_variables["ENABLE_PIC"] = "ON" if self.options.get_safe("fPIC", True) else "OFF"
        # Avoid to install vc runtime stuff
        tc.variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = "TRUE"
        if self.options.with_ssl == "openssl":
            tc.variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder
        if Version(self.version) >= "1.20.0":
            tc.variables["MONGO_USE_CCACHE"] = False
        if is_msvc(self):
            # Should be added because of
            # https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-initonceexecuteonce
            tc.preprocessor_definitions["_WIN32_WINNT"] = "0x0600"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        if self.options.with_ssl == "libressl" or self.options.with_zstd:
            deps = PkgConfigDeps(self)
            deps.generate()
            env = VirtualBuildEnv(self)
            env.generate()
            # TODO: to remove when properly handled by conan (see https://github.com/conan-io/conan/issues/11962)
            env = Environment()
            env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
            envvars = env.vars(self)
            envvars.save_script("conanbuildenv_pkg_config_path")

    def _patch_sources(self):
        apply_conandata_patches(self)
        to_replace_old_new = [
            # Fix Snappy
            {"old": "include (FindSnappy)\nif (SNAPPY_INCLUDE_DIRS)",
             "new": "if(ENABLE_SNAPPY MATCHES \"ON\")\n  find_package(Snappy REQUIRED)"},
            {"old": "SNAPPY_LIBRARIES", "new": "Snappy_LIBRARIES"},
            {"old": "SNAPPY_INCLUDE_DIRS", "new": "Snappy_INCLUDE_DIRS"},
            # Fix LibreSSL
            {"old": "set (SSL_LIBRARIES -ltls -lcrypto)", "new": ""},
        ]
        for old_new in to_replace_old_new:
            replace_in_file(self, os.path.join(self.source_folder, "src", "libmongoc", "CMakeLists.txt"),
                                  old_new["old"], old_new["new"])
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
        mongoc_target = "mongoc_shared" if self.options.shared else "mongoc_static"
        self.cpp_info.set_property("cmake_file_name", "mongoc-1.0")
        self.cpp_info.set_property("cmake_target_name", f"mongo::{mongoc_target}")

        self.cpp_info.filenames["cmake_find_package"] = "mongoc-1.0"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mongoc-1.0"
        self.cpp_info.names["cmake_find_package"] = "mongo"
        self.cpp_info.names["cmake_find_package_multi"] = "mongo"

        # mongoc
        self.cpp_info.components["mongoc"].set_property("cmake_target_name", f"mongo::{mongoc_target}")
        self.cpp_info.components["mongoc"].set_property("pkg_config_name", "libmongoc-1.0" if self.options.shared else "libmongoc-static-1.0")

        self.cpp_info.components["mongoc"].names["cmake_find_package"] = mongoc_target
        self.cpp_info.components["mongoc"].names["cmake_find_package_multi"] = mongoc_target

        self.cpp_info.components["mongoc"].includedirs = [os.path.join("include", "libmongoc-1.0")]
        self.cpp_info.components["mongoc"].libs = ["mongoc-1.0" if self.options.shared else "mongoc-static-1.0"]
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
        bson_target = "bson_shared" if self.options.shared else "bson_static"
        self.cpp_info.components["bson"].set_property("cmake_target_name", f"mongo::{bson_target}")
        self.cpp_info.components["bson"].set_property("pkg_config_name", "libbson-1.0" if self.options.shared else "libbson-static-1.0")

        self.cpp_info.components["bson"].names["cmake_find_package"] = bson_target
        self.cpp_info.components["bson"].names["cmake_find_package_multi"] = bson_target

        self.cpp_info.components["bson"].includedirs = [os.path.join("include", "libbson-1.0")]
        self.cpp_info.components["bson"].libs = ["bson-1.0" if self.options.shared else "bson-static-1.0"]
        if not self.options.shared:
            self.cpp_info.components["bson"].defines = ["BSON_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["bson"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["bson"].system_libs = ["ws2_32"]

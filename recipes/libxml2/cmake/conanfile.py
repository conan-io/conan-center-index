import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, cmake_layout, CMakeToolchain
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version


class Libxml2Conan(ConanFile):
    name = "libxml2"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml2 is a software library for parsing XML documents"
    topics = "xml", "parser", "validation"
    homepage = "https://gitlab.gnome.org/GNOME/libxml2/-/wikis/"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "catalog": [True, False],
        "debug": [True, False],
        "html": [True, False],
        "http": [True, False],
        "iconv": [True, False],
        "icu": [True, False],
        "iso8859x": [True, False],
        "legacy": [True, False],
        "lzma": [True, False],
        "modules": [True, False],
        "output": [True, False],
        "pattern": [True, False],
        "programs": [True, False],
        "push": [True, False],
        "python": [True, False],
        "readline": [True, False],
        "regexps": [True, False],
        "sax1": [True, False],
        "threads": [True, False],
        "tls": [True, False],
        "valid": [True, False],
        "xinclude": [True, False],
        "xpath": [True, False],
        "zlib": [True, False],
        "c14n": [True, False],
        "history": [True, False],
        "schemas": [True, False],
        "schematron": [True, False],
        "thread_alloc": [True, False],
        "writer": [True, False],
        "xptr": [True, False],
        "relaxng": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "catalog": True,
        "debug": True,
        "html": True,
        "http": True,
        "iconv": True,
        "icu": False,
        "iso8859x": True,
        "legacy": False,
        "lzma": False,
        "modules": True,
        "output": True,
        "pattern":  True,
        "programs": True,
        "push": True,
        "python": False,
        "readline": False,
        "regexps": True,
        "sax1": True,
        "threads": True,
        "tls": False,
        "valid": True,
        "xinclude": True,
        "xpath": True,
        "zlib": True,
        "c14n": True,
        "history": False,
        "schemas": True,
        "schematron": True,
        "thread_alloc": False,
        "writer": True,
        "xptr": True,
        "relaxng": True
    }
    languages = "C"
    implements = ["auto_shared_fpic"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "2.15.0":
            del self.options.lzma

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.iconv:
            self.requires("libiconv/1.17")
        if self.options.get_safe("lzma"):
            self.requires("xz_utils/[>=5.4.5 <6]")
        if self.options.icu:
            self.requires("icu/73.2")
        if self.options.zlib:
            self.requires("zlib/[>=1.3.1 <2]")

        self.tool_requires("cmake/[>=3.18]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["LIBXML2_WITH_CATALOG"] = self.options.catalog
        tc.cache_variables["LIBXML2_WITH_DEBUG"] = self.options.debug
        tc.cache_variables["LIBXML2_WITH_HTML"] = self.options.html
        tc.cache_variables["LIBXML2_WITH_HTTP"] = self.options.http
        tc.cache_variables["LIBXML2_WITH_ICONV"] = self.options.iconv
        tc.cache_variables["LIBXML2_WITH_ICU"] = self.options.icu
        tc.cache_variables["LIBXML2_WITH_ISO8859X"] = self.options.iso8859x
        tc.cache_variables["LIBXML2_WITH_LEGACY"] = self.options.legacy
        if "lzma" in self.options:  # removed since 2.15.0
            tc.cache_variables["LIBXML2_WITH_LZMA"] = self.options.lzma
        tc.cache_variables["LIBXML2_WITH_MODULES"] = self.options.modules
        tc.cache_variables["LIBXML2_WITH_OUTPUT"] = self.options.output
        tc.cache_variables["LIBXML2_WITH_PATTERN"] = self.options.pattern
        tc.cache_variables["LIBXML2_WITH_PROGRAMS"] = self.options.programs
        tc.cache_variables["LIBXML2_WITH_PUSH"] = self.options.push
        tc.cache_variables["LIBXML2_WITH_PYTHON"] = self.options.python
        tc.cache_variables["LIBXML2_WITH_READLINE"] = self.options.readline
        tc.cache_variables["LIBXML2_WITH_REGEXPS"] = self.options.regexps
        tc.cache_variables["LIBXML2_WITH_SAX1"] = self.options.sax1
        tc.cache_variables["LIBXML2_WITH_THREADS"] = self.options.threads
        tc.cache_variables["LIBXML2_WITH_TLS"] = self.options.tls
        tc.cache_variables["LIBXML2_WITH_VALID"] = self.options.valid
        tc.cache_variables["LIBXML2_WITH_XINCLUDE"] = self.options.xinclude
        tc.cache_variables["LIBXML2_WITH_XPATH"] = self.options.xpath
        tc.cache_variables["LIBXML2_WITH_ZLIB"] = self.options.zlib
        tc.cache_variables["LIBXML2_WITH_C14N"] = self.options.c14n
        tc.cache_variables["LIBXML2_WITH_HISTORY"] = self.options.history
        tc.cache_variables["LIBXML2_WITH_SCHEMAS"] = self.options.schemas
        tc.cache_variables["LIBXML2_WITH_SCHEMATRON"] = self.options.schematron
        tc.cache_variables["LIBXML2_WITH_THREAD_ALLOC"] = self.options.thread_alloc
        tc.cache_variables["LIBXML2_WITH_WRITER"] = self.options.writer
        tc.cache_variables["LIBXML2_WITH_XPTR"] = self.options.xptr
        tc.cache_variables["LIBXML2_WITH_RELAXNG"] = self.options.relaxng

        # inhibit any CMake logic that requires pkg-config
        tc.cache_variables["PKG_CONFIG_EXECUTABLE"] = "PKG_CONFIG_EXECUTABLE-NOTFOUND"
        tc.cache_variables["LIBXML2_WITH_TESTS"] = False
        tc.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "Copyright", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share")) # contains manpages and docs - if needed, please open an issue

    def package_info(self):
        postfix = ""
        prefix = "lib" if self.settings.os == "Windows" else ""
        # compiler.runtime distinguishes clang-cl (has MSVC runtime, e.g. "dynamic") from clang targeting libc++ (no compiler.runtime setting)
        msvc_like = self.settings.os == "Windows" and self.settings.compiler in ["msvc", "clang"] and self.settings.get_safe("compiler.runtime")
        if msvc_like:
            static_postfix = "s" if not self.options.shared else ""
            debug_postfix = "d" if self.settings.build_type == "Debug" else ""
            postfix = f"{static_postfix}{debug_postfix}"
            
        self.cpp_info.libs = [f"{prefix}xml2{postfix}"]

        # technically there should be a single include directory, but this
        # keeps compatibility with the .pc files generated upstream (and relied on by ffmpeg)
        self.cpp_info.includedirs.append(os.path.join("include", "libxml2"))
        
        if not self.options.shared:
            self.cpp_info.defines.append("LIBXML_STATIC")

        self.cpp_info.set_property("cmake_file_name", "libxml2")
        self.cpp_info.set_property("cmake_target_name", "LibXml2::LibXml2")
        self.cpp_info.set_property("cmake_additional_variables_prefixes", ["LIBXML2"])
        self.cpp_info.set_property("pkg_config_name", "libxml-2.0")

        is_unix = self.settings.os in ["Linux", "FreeBSD", "Macos", "Android"] or is_apple_os(self)

        if is_unix:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("dl")

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")

        if self.options.icu:
            self.cpp_info.requires.extend(["icu::icu-uc", "icu::icu-data", "icu::icu-i18n"])
        if self.options.iconv:
            self.cpp_info.requires.append("libiconv::libiconv")
        if self.options.get_safe("lzma"):
            self.cpp_info.requires.append("xz_utils::xz_utils")
        if self.options.zlib:
            self.cpp_info.requires.append("zlib::zlib")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("Bcrypt")
            self.cpp_info.system_libs.append("ws2_32") # http

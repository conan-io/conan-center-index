from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=1.50.0"


class PCREConan(ConanFile):
    name = "pcre"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org"
    description = "Perl Compatible Regular Expressions"
    topics = ("regex", "regexp", "PCRE")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_pcre_8": [True, False],
        "build_pcre_16": [True, False],
        "build_pcre_32": [True, False],
        "build_pcrecpp": [True, False],
        "build_pcregrep": [True, False],
        "with_bzip2": [True, False],
        "with_zlib": [True, False],
        "with_jit": [True, False],
        "with_utf": [True, False],
        "with_unicode_properties": [True, False],
        "with_stack_for_recursion": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_pcre_8": True,
        "build_pcre_16": True,
        "build_pcre_32": True,
        "build_pcrecpp": False,
        "build_pcregrep": True,
        "with_bzip2": True,
        "with_zlib": True,
        "with_jit": False,
        "with_utf": True,
        "with_unicode_properties": True,
        "with_stack_for_recursion": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.build_pcrecpp:
            try:
                del self.settings.compiler.libcxx
            except Exception:
                pass
            try:
                del self.settings.compiler.cppstd
            except Exception:
                pass
        if not self.options.build_pcregrep:
            del self.options.with_bzip2
            del self.options.with_zlib
        if self.options.with_unicode_properties:
            self.options.with_utf = True

    def requirements(self):
        if self.options.get_safe("with_bzip2"):
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.12")

    def validate(self):
        if not self.info.options.build_pcre_8 and not self.info.options.build_pcre_16 and not self.info.options.build_pcre_32:
            raise ConanInvalidConfiguration("At least one of build_pcre_8, build_pcre_16 or build_pcre_32 must be enabled")
        if self.info.options.build_pcrecpp and not self.info.options.build_pcre_8:
            raise ConanInvalidConfiguration("build_pcre_8 must be enabled for the C++ library support")
        if self.info.options.build_pcregrep and not self.info.options.build_pcre_8:
            raise ConanInvalidConfiguration("build_pcre_8 must be enabled for the pcregrep program")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PCRE_BUILD_TESTS"] = False
        tc.variables["PCRE_BUILD_PCRE8"] = self.options.build_pcre_8
        tc.variables["PCRE_BUILD_PCRE16"] = self.options.build_pcre_16
        tc.variables["PCRE_BUILD_PCRE32"] = self.options.build_pcre_32
        tc.variables["PCRE_BUILD_PCREGREP"] = self.options.build_pcregrep
        tc.variables["PCRE_BUILD_PCRECPP"] = self.options.build_pcrecpp
        tc.variables["PCRE_SUPPORT_LIBZ"] = self.options.get_safe("with_zlib", False)
        tc.variables["PCRE_SUPPORT_LIBBZ2"] = self.options.get_safe("with_bzip2", False)
        tc.variables["PCRE_SUPPORT_JIT"] = self.options.with_jit
        tc.variables["PCRE_SUPPORT_UTF"] = self.options.with_utf
        tc.variables["PCRE_SUPPORT_UNICODE_PROPERTIES"] = self.options.with_unicode_properties
        tc.variables["PCRE_SUPPORT_LIBREADLINE"] = False
        tc.variables["PCRE_SUPPORT_LIBEDIT"] = False
        tc.variables["PCRE_NO_RECURSE"] = not self.options.with_stack_for_recursion
        if is_msvc(self):
            tc.variables["PCRE_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Honor BUILD_SHARED_LIBS since upstream CMakeLists overrides it as a CACHE variable.
        # Issue quite similar to https://github.com/conan-io/conan/issues/11840
        tc.cache_variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmake_file = os.path.join(self.source_folder, "CMakeLists.txt")
        # Avoid man and share during install stage
        replace_in_file(self, cmake_file, "INSTALL(FILES ${man1} DESTINATION man/man1)", "")
        replace_in_file(self, cmake_file, "INSTALL(FILES ${man3} DESTINATION man/man3)", "")
        replace_in_file(self, cmake_file, "INSTALL(FILES ${html} DESTINATION share/doc/pcre/html)", "")
        # Do not override CMAKE_MODULE_PATH and do not add ${PROJECT_SOURCE_DIR}/cmake
        # because it contains a custom FindPackageHandleStandardArgs.cmake which
        # can break conan generators
        replace_in_file(self, cmake_file, "SET(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)", "")
        # Avoid CMP0006 error (macos bundle)
        replace_in_file(
            self,
            cmake_file,
            "RUNTIME DESTINATION bin",
            "RUNTIME DESTINATION bin\n        BUNDLE DESTINATION bin",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENCE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

        if self.options.build_pcre_8:
            # pcre
            self.cpp_info.components["libpcre"].set_property("pkg_config_name", "libpcre")
            self.cpp_info.components["libpcre"].libs = [f"pcre{suffix}"]
            if not self.options.shared:
                self.cpp_info.components["libpcre"].defines.append("PCRE_STATIC=1")
            # pcreposix
            self.cpp_info.components["libpcreposix"].set_property("pkg_config_name", "libpcreposix")
            self.cpp_info.components["libpcreposix"].libs = [f"pcreposix{suffix}"]
            self.cpp_info.components["libpcreposix"].requires = ["libpcre"]
            # pcrecpp
            if self.options.build_pcrecpp:
                self.cpp_info.components["libpcrecpp"].set_property("pkg_config_name", "libpcrecpp")
                self.cpp_info.components["libpcrecpp"].libs = [f"pcrecpp{suffix}"]
                self.cpp_info.components["libpcrecpp"].requires = ["libpcre"]
        # pcre16
        if self.options.build_pcre_16:
            self.cpp_info.components["libpcre16"].set_property("pkg_config_name", "libpcre16")
            self.cpp_info.components["libpcre16"].libs = [f"pcre16{suffix}"]
            if not self.options.shared:
                self.cpp_info.components["libpcre16"].defines.append("PCRE_STATIC=1")
        # pcre32
        if self.options.build_pcre_32:
            self.cpp_info.components["libpcre32"].set_property("pkg_config_name", "libpcre32")
            self.cpp_info.components["libpcre32"].libs = [f"pcre32{suffix}"]
            if not self.options.shared:
                self.cpp_info.components["libpcre32"].defines.append("PCRE_STATIC=1")

        if self.options.build_pcregrep:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
            # FIXME: This is a workaround to avoid ConanException. zlib and bzip2
            # are optional requirements of pcregrep executable, not of any pcre lib.
            if self.options.with_bzip2:
                self.cpp_info.components["libpcre"].requires.append("bzip2::bzip2")
            if self.options.with_zlib:
                self.cpp_info.components["libpcre"].requires.append("zlib::zlib")

        # TODO: to remove in conan v2 once legacy generators removed
        #       DO NOT port this name to cmake_file_name/cmake_target_name properties, it was a mistake
        self.cpp_info.names["cmake_find_package"] = "PCRE"
        self.cpp_info.names["cmake_find_package_multi"] = "PCRE"

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class PCRE2Conan(ConanFile):
    name = "pcre2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org/"
    description = "Perl Compatible Regular Expressions"
    topics = ("regex", "regexp", "perl")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_pcre2_8": [True, False],
        "build_pcre2_16": [True, False],
        "build_pcre2_32": [True, False],
        "build_pcre2grep": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "support_jit": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_pcre2_8": True,
        "build_pcre2_16": True,
        "build_pcre2_32": True,
        "build_pcre2grep": True,
        "with_zlib": True,
        "with_bzip2": True,
        "support_jit": False,
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
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass
        if not self.options.build_pcre2grep:
            del self.options.with_zlib
            del self.options.with_bzip2

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.12")
        if self.options.get_safe("with_bzip2"):
            self.requires("bzip2/1.0.8")

    def validate(self):
        if not self.info.options.build_pcre2_8 and not self.info.options.build_pcre2_16 and not self.info.options.build_pcre2_32:
            raise ConanInvalidConfiguration("At least one of build_pcre2_8, build_pcre2_16 or build_pcre2_32 must be enabled")
        if self.info.options.build_pcre2grep and not self.info.options.build_pcre2_8:
            raise ConanInvalidConfiguration("build_pcre2_8 must be enabled for the pcre2grep program")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Mandatory because upstream CMakeLists overrides BUILD_SHARED_LIBS as a CACHE variable
        # (see https://github.com/conan-io/conan/issues/11840)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        if Version(self.version) >= "10.38":
            tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["PCRE2_BUILD_PCRE2GREP"] = self.options.build_pcre2grep
        tc.variables["PCRE2_SUPPORT_LIBZ"] = self.options.get_safe("with_zlib", False)
        tc.variables["PCRE2_SUPPORT_LIBBZ2"] = self.options.get_safe("with_bzip2", False)
        tc.variables["PCRE2_BUILD_TESTS"] = False
        if is_msvc(self):
            tc.variables["PCRE2_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.variables["PCRE2_DEBUG"] = self.settings.build_type == "Debug"
        tc.variables["PCRE2_BUILD_PCRE2_8"] = self.options.build_pcre2_8
        tc.variables["PCRE2_BUILD_PCRE2_16"] = self.options.build_pcre2_16
        tc.variables["PCRE2_BUILD_PCRE2_32"] = self.options.build_pcre2_32
        tc.variables["PCRE2_SUPPORT_JIT"] = self.options.support_jit
        if Version(self.version) < "10.38":
            # relocatable shared libs on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Do not add ${PROJECT_SOURCE_DIR}/cmake because it contains a custom
        # FindPackageHandleStandardArgs.cmake which can break conan generators
        if Version(self.version) < "10.34":
            replace_in_file(self, cmakelists, "SET(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)", "")
        else:
            replace_in_file(self, cmakelists, "LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)", "")
        # Avoid CMP0006 error (macos bundle)
        replace_in_file(self, cmakelists,
                              "RUNTIME DESTINATION bin",
                              "RUNTIME DESTINATION bin BUNDLE DESTINATION bin")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENCE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "man"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PCRE2")
        self.cpp_info.set_property("pkg_config_name", "libpcre2")
        if self.options.build_pcre2_8:
            # pcre2-8
            self.cpp_info.components["pcre2-8"].set_property("cmake_target_name", "PCRE2::8BIT")
            self.cpp_info.components["pcre2-8"].set_property("pkg_config_name", "libpcre2-8")
            self.cpp_info.components["pcre2-8"].libs = [self._lib_name("pcre2-8")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-8"].defines.append("PCRE2_STATIC")
            # pcre2-posix
            self.cpp_info.components["pcre2-posix"].set_property("cmake_target_name", "PCRE2::POSIX")
            self.cpp_info.components["pcre2-posix"].set_property("pkg_config_name", "libpcre2-posix")
            self.cpp_info.components["pcre2-posix"].libs = [self._lib_name("pcre2-posix")]
            self.cpp_info.components["pcre2-posix"].requires = ["pcre2-8"]
        # pcre2-16
        if self.options.build_pcre2_16:
            self.cpp_info.components["pcre2-16"].set_property("cmake_target_name", "PCRE2::16BIT")
            self.cpp_info.components["pcre2-16"].set_property("pkg_config_name", "libpcre2-16")
            self.cpp_info.components["pcre2-16"].libs = [self._lib_name("pcre2-16")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-16"].defines.append("PCRE2_STATIC")
        # pcre2-32
        if self.options.build_pcre2_32:
            self.cpp_info.components["pcre2-32"].set_property("cmake_target_name", "PCRE2::32BIT")
            self.cpp_info.components["pcre2-32"].set_property("pkg_config_name", "libpcre2-32")
            self.cpp_info.components["pcre2-32"].libs = [self._lib_name("pcre2-32")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-32"].defines.append("PCRE2_STATIC")

        if self.options.build_pcre2grep:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
            # FIXME: This is a workaround to avoid ConanException. zlib and bzip2
            # are optional requirements of pcre2grep executable, not of any pcre2 lib.
            if self.options.with_zlib:
                self.cpp_info.components["pcre2-8"].requires.append("zlib::zlib")
            if self.options.with_bzip2:
                self.cpp_info.components["pcre2-8"].requires.append("bzip2::bzip2")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generator removed
        self.cpp_info.names["cmake_find_package"] = "PCRE2"
        self.cpp_info.names["cmake_find_package_multi"] = "PCRE2"
        self.cpp_info.names["pkg_config"] = "libpcre2"
        if self.options.build_pcre2_8:
            self.cpp_info.components["pcre2-8"].names["cmake_find_package"] = "8BIT"
            self.cpp_info.components["pcre2-8"].names["cmake_find_package_multi"] = "8BIT"
            self.cpp_info.components["pcre2-posix"].names["cmake_find_package"] = "POSIX"
            self.cpp_info.components["pcre2-posix"].names["cmake_find_package_multi"] = "POSIX"
        if self.options.build_pcre2_16:
            self.cpp_info.components["pcre2-16"].names["cmake_find_package"] = "16BIT"
            self.cpp_info.components["pcre2-16"].names["cmake_find_package_multi"] = "16BIT"
        if self.options.build_pcre2_32:
            self.cpp_info.components["pcre2-32"].names["cmake_find_package"] = "32BIT"
            self.cpp_info.components["pcre2-32"].names["cmake_find_package_multi"] = "32BIT"

    def _lib_name(self, name):
        libname = name
        if Version(self.version) >= "10.38" and is_msvc(self) and not self.options.shared:
            libname += "-static"
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                libname += "d"
            if self.settings.compiler == "gcc" and self.options.shared:
                libname += ".dll"
        return libname

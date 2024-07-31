import os

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, valid_min_cppstd, can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


class LibphonenumberConan(ConanFile):
    name = "libphonenumber"
    description = "Google's common C++ library for parsing, formatting, and validating international phone numbers"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/libphonenumber"
    topics = ("phone-numbers", "phone")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_geocoder": [True, False],
        "use_alternate_formats": [True, False],
        "use_boost": [True, False],
        "use_icu_regexp": [True, False],
        "use_lite_metadata": [True, False],
        "use_posix_thread": [True, False],
        "use_std_mutex": [True, False],
        #re2 is not an option, because using it crashes
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_geocoder": True,
        "use_alternate_formats": True,
        "use_boost": False,
        "use_icu_regexp": True,
        "use_lite_metadata": False,
        "use_posix_thread": False,
        "use_std_mutex": True,
    }
    options_description = {
       "build_geocoder": "Build the offline phone number geocoder",
       "use_alternate_formats": "Use alternate formats for the phone number matcher.",
       "use_icu_regexp": "Use ICU regexp engine",
       "use_lite_metadata": "Generates smaller metadata that doesn't include example numbers",
       "use_posix_thread": "Use Posix thread for multi-threading",
       "use_std_mutex": "use C++ 2011 std::mutex for multi-threading",
    }

    @property
    def _min_cppstd(self):
        return 11 if Version(self.dependencies["abseil"].ref.version) < "20230125.0" else 14

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # TODO: could use pthread4w
            del self.options.use_posix_thread
        if not can_run(self):
            # otherwise fails when trying to build and run generate_geocoding_data
            del self.options.build_geocoder

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/google/libphonenumber/blob/v8.13.35/cpp/src/phonenumbers/phonenumberutil.h#L33-L34
        self.requires("abseil/20240116.2", transitive_headers=True)
        self.requires("protobuf/5.27.0", transitive_headers=True, transitive_libs=True)
        if self.options.use_boost:
            # https://github.com/google/libphonenumber/blob/v8.13.35/cpp/src/phonenumbers/base/synchronization/lock_boost.h
            self.requires("boost/1.85.0", transitive_headers=True, transitive_libs=True)
        if self.options.use_icu_regexp or self.options.get_safe("build_geocoder"):
            # https://github.com/google/libphonenumber/blob/v8.13.35/cpp/src/phonenumbers/geocoding/phonenumber_offline_geocoder.h#L23
            self.requires("icu/75.1", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.name} not supported in Windows yet, contributions welcome\n"
                                            "https://github.com/google/libphonenumber/blob/master/FAQ.md#what-about-windows")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if not self.options.use_std_mutex and not self.options.use_boost and not self.options.get_safe("use_posix_thread"):
            raise ConanInvalidConfiguration("At least one of use_std_mutex, use_boost or use_posix_thread must be enabled")

        if not self.options.use_icu_regexp:
            # Fails with 'undefined reference to `vtable for i18n::phonenumbers::ICURegExpFactory''
            raise ConanInvalidConfiguration("use_icu_regexp=False is not supported")

        if conan_version.major == 1:
            raise ConanInvalidConfiguration("Conan 1.x is not supported. Contributions are welcome!")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.2.0")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIB"] = not self.options.shared
        tc.variables["BUILD_GEOCODER"] = self.options.get_safe("build_geocoder", False)
        tc.variables["USE_ALTERNATE_FORMATS"] = self.options.use_alternate_formats
        tc.variables["USE_BOOST"] = self.options.use_boost
        tc.variables["USE_ICU_REGEXP"] = self.options.use_icu_regexp
        tc.variables["USE_LITE_METADATA"] = self.options.use_lite_metadata
        tc.variables["USE_POSIX_THREAD"] = self.options.get_safe("use_posix_thread", False)
        tc.variables["USE_PROTOBUF_LITE"] = self.dependencies["protobuf"].options.lite
        tc.variables["USE_RE2"] = False  # Hardcoded, attempt to use it crashed
        tc.variables["USE_STDMUTEX"] = self.options.use_std_mutex
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_TOOLS_ONLY"] = False
        tc.variables["REGENERATE_METADATA"] = False  # Requires a Java runtime
        # Otherwise tries to use <tr1/unordered_map>, and requires the recipe to export a define accordingly.
        # The define can be set based only on a compilation test.
        tc.variables["USE_STD_MAP"] = True
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # (failed) attempt to make it work in windows/msvc, patching some build scripts
        # https://github.com/conan-io/conan-center-index/pull/23689/commits/c5e7091d134174fb590218ed066c074f45274a93
        replace_in_file(self, os.path.join(self.source_folder, "cpp", "CMakeLists.txt"), " -Werror", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "cpp"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.components["phonenumber"].set_property("cmake_target_aliases", ["libphonenumber::phonenumber-shared"])
        self.cpp_info.components["phonenumber"].libs = ["phonenumber"]
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.use_posix_thread:
            self.cpp_info.components["phonenumber"].system_libs.append("pthread")
        elif is_apple_os(self):
            self.cpp_info.components["phonenumber"].frameworks.extend(["CoreFoundation", "Foundation"])

        requires = ["abseil::absl_node_hash_set", "abseil::absl_strings", "abseil::absl_synchronization"]
        if self.dependencies["protobuf"].options.lite:
            requires.append("protobuf::libprotobuf-lite")
        else:
            requires.append("protobuf::libprotobuf")
        if self.options.use_boost:
            requires.extend(["boost::headers", "boost::thread"])
        if self.options.use_icu_regexp:
            requires.extend(["icu::icu-uc", "icu::icu-i18n"])
        self.cpp_info.components["phonenumber"].requires = requires

        if self.options.get_safe("build_geocoder"):
            if self.options.shared:
                self.cpp_info.components["geocoding"].set_property("cmake_target_aliases", ["libphonenumber::geocoding-shared"])
            self.cpp_info.components["geocoding"].libs.append("geocoding")
            self.cpp_info.components["geocoding"].requires = ["abseil::absl_synchronization", "icu::icu-uc"]

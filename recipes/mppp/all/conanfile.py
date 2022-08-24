from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

import os
import functools

required_conan_version = ">=1.43.0"

class MpppConan(ConanFile):
    name = "mppp"
    description = "Multiprecision for modern C++ Topics"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bluescarni/mppp/"
    topics = ("multiprecision", "gmp", "math-bignum", "computer-algebra")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mpfr": [True, False],
        "with_arb": [True, False],
        "with_mpc": [True, False],
        "with_quadmath": [True, False],
        "with_boost": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mpfr": False,
        "with_arb": False,
        "with_mpc": False,
        "with_quadmath": False,
        "with_boost": False,
    }
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("gmp/6.2.1")
        if self.options.with_mpfr == True:
            self.requires("mpfr/4.1.0")
        if self.options.with_mpc == True:
            self.requires("mpc/1.2.0")
        if self.options.with_boost == True:
            self.requires("boost/1.79.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.options.with_arb:
            raise ConanInvalidConfiguration("{}/{} doesn't supported arb (yet)".format(self.name, self.version))
        if self.options.with_quadmath:
            raise ConanInvalidConfiguration("{}/{} doesn't supported libquadmath (yet)".format(self.name, self.version))
        if self.options.with_boost and self.options["boost"].without_serialization:
            raise ConanInvalidConfiguration("{}:with_boost=True requires boost::without_serialization=False".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["MPPP_BUILD_STATIC_LIBRARY"] = not self.options.shared
        cmake.definitions["MPPP_WITH_MPFR"] = self.options.with_mpfr
        cmake.definitions["MPPP_WITH_ARB"] = self.options.with_arb
        cmake.definitions["MPPP_WITH_MPC"] = self.options.with_mpc
        cmake.definitions["MPPP_WITH_QUADMATH"] = self.options.with_quadmath
        cmake.definitions["MPPP_WITH_BOOST_S11N"] = self.options.with_boost
        if not self.options.shared:
            cmake.definitions["MPPP_BUILD_STATIC_LIBRARY_WITH_DYNAMIC_MSVC_RUNTIME"] = self.settings.compiler.get_safe("runtime") in ["MD", "MDd"]
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["mp++"]
        self.cpp_info.set_property("cmake_file_name", "mp++")
        self.cpp_info.set_property("cmake_target_name", "mp++::mp++")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mp++"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mp++"
        self.cpp_info.names["cmake_find_package"] = "mp++"
        self.cpp_info.names["cmake_find_package_multi"] = "mp++"

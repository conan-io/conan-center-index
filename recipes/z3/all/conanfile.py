from conans import CMake, ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class Z3Conan(ConanFile):
    name = "z3"
    description = "The Z3 Theorem Prover"
    topics = ("z3", "theorem", "SMT", "satisfiability", "prover", "solver")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Z3Prover/z3"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "multithreaded": [True, False],
        "multiprecision": ["internal", "gmp", "mpir"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "multithreaded": True,
        "multiprecision": "gmp"
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        if self.options.multiprecision == "internal":
            self.provides.append("gmp")

    def requirements(self):
        self.output.info(
            f"{self.name} will build using {self.options.multiprecision} multiprecision implementation.")
        if self.options.multiprecision == "mpir":
            self.requires("mpir/3.0.0")
        elif self.options.multiprecision == "gmp":
            self.requires("gmp/6.2.1")
        elif self.options.multiprecision == "internal":
            pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["Z3_USE_LIB_GMP"] = self.options.multiprecision != "internal"
        self._cmake.definitions["Z3_USE_LIB_MPIR"] = self.options.multiprecision == "mpir"
        self._cmake.definitions["SINGLE_THREADED"] = not self.options.multithreaded
        self._cmake.definitions["Z3_BUILD_LIBZ3_SHARED"] = self.options.shared
        self._cmake.definitions["Z3_INCLUDE_GIT_HASH"] = False
        self._cmake.definitions["Z3_INCLUDE_GIT_DESCRIBE"] = False
        self._cmake.definitions["Z3_ENABLE_EXAMPLE_TARGETS"] = False
        self._cmake.definitions["Z3_BUILD_DOCUMENTATION"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if tools.Version(self.version) >= tools.Version("4.8.11"):
            if self.settings.compiler.get_safe("cppstd"):
                tools.check_min_cppstd(self, "17")
            compiler = self.settings.compiler
            min_version = self._compilers_minimum_version\
                .get(str(compiler), False)
            if min_version:
                if tools.Version(compiler.version) < min_version:
                    raise ConanInvalidConfiguration(
                        f"{self.name} requires C++17, which {compiler} {compiler.version} does not support.")
            else:
                self.output.info(
                    f"{self.name} requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        if self.options.multiprecision == "mpir":
            tools.save(os.path.join(self._build_subfolder, "gmp.h"), textwrap.dedent("""\
                #pragma once
                #include <mpir.h>
                """))

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Z3")
        self.cpp_info.set_property("cmake_target_name", "z3::libz3")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libz3"].libs = [
            "libz3" if self.settings.os == "Windows" else "z3"]
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libz3"]\
                    .system_libs.extend(["pthread", "m"])
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Z3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Z3"
        self.cpp_info.names["cmake_find_package"] = "z3"
        self.cpp_info.names["cmake_find_package_multi"] = "z3"
        self.cpp_info.components["libz3"].names["cmake_find_package"] = "libz3"
        self.cpp_info.components["libz3"].names["cmake_find_package_multi"] = "libz3"
        self.cpp_info.components["libz3"].set_property(
            "cmake_target_name", "z3::libz3")

        libz3_requirements = []
        if self.options.multiprecision == "mpir":
            libz3_requirements.append("mpir::mpir")
        elif self.options.multiprecision == "gmp":
            libz3_requirements.append("gmp::gmp")
        elif self.options.multiprecision == "internal":
            pass
        self.cpp_info.components["libz3"].requires = libz3_requirements

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
import os
import textwrap
import functools

required_conan_version = ">=1.43.0"


class TesseractConan(ConanFile):
    name = "tesseract"
    description = "Tesseract Open Source OCR Engine"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tesseract-ocr/tesseract"
    topics = ("ocr", "image", "multimedia", "graphics")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_auto_optimize": [True, False],
        "with_march_native": [True, False],
        "with_training": [True, False],
        "with_libcurl": [True, False],
        "with_libarchive": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_auto_optimize": False,
        "with_march_native": False,
        "with_training": False,
        "with_libcurl": True,
        "with_libarchive": True,
    }

    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

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
        if tools.Version(self.version) < "5.0.0":
            del self.options.with_libcurl
            del self.options.with_libarchive

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_training:
            # do not enforce failure and allow user to build with system cairo, pango, fontconfig
            self.output.warn("*** Build with training is not yet supported, continue on your own")

    def requirements(self):
        self.requires("leptonica/1.82.0")
        # libarchive is required for 4.x so default value is true
        if self.options.get_safe("with_libarchive", default=True):
            self.requires("libarchive/3.6.1")
        # libcurl is not required for 4.x
        if self.options.get_safe("with_libcurl", default=False):
            self.requires("libcurl/7.84.0")

    def validate(self):
        # Check compiler version
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version.value)

        if tools.Version(self.version) >= "5.0.0":
            # 5.0.0 requires C++-17 compiler
            minimal_version = {
                "Visual Studio": "16",
                "gcc": "7",
                "clang": "7",
                "apple-clang": "11"
            }
        else:
            minimal_version = {
                "Visual Studio": "14",
                "gcc": "5",
                "clang": "5",
                "apple-clang": "6"
            }
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
        elif compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a {} version >= {}, but {} was found".format(self.name, compiler, minimal_version[compiler], compiler_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TRAINING_TOOLS"] = self.options.with_training
        cmake.definitions["INSTALL_CONFIGS"] = self.options.with_training

        # pre-5.0.0 uses custom STATIC variable instead of BUILD_SHARED_LIBS
        if tools.Version(self.version) < "5.0.0":
            cmake.definitions["STATIC"] = not self.options.shared

        # Use CMake-based package build and dependency detection, not the pkg-config, cppan or SW
        cmake.definitions["CPPAN_BUILD"] = False
        cmake.definitions["SW_BUILD"] = False

        # disable autodetect of vector extensions and march=native
        cmake.definitions["ENABLE_OPTIMIZATIONS"] = self.options.with_auto_optimize

        if tools.Version(self.version) < "5.0.0":
            cmake.definitions["AUTO_OPTIMIZE"] = self.options.with_auto_optimize

        # Set Leptonica_DIR to ensure that find_package will be called in original CMake file
        cmake.definitions["Leptonica_DIR"] = self.deps_cpp_info["leptonica"].rootpath

        if tools.Version(self.version) >= "5.0.0":
            cmake.definitions["DISABLE_CURL"] = not self.options.with_libcurl
            cmake.definitions["DISABLE_ARCHIVE"] = not self.options.with_libarchive

        if cross_building(self):
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            cmake.definitions["CONAN_TESSERACT_SYSTEM_PROCESSOR"] = cmake_system_processor

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"libtesseract": "Tesseract::libtesseract"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        # Official CMake imported target is:
        # - libtesseract if < 5.0.0
        # - Tesseract::libtesseract if >= 5.0.0 (not yet released)
        # We provide both targets
        self.cpp_info.set_property("cmake_file_name", "Tesseract")
        self.cpp_info.set_property("cmake_target_name", "Tesseract::libtesseract")
        self.cpp_info.set_property("cmake_target_aliases", ["libtesseract"])
        self.cpp_info.set_property("pkg_config_name", "tesseract")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libtesseract"].libs = [self._libname]
        self.cpp_info.components["libtesseract"].requires = ["leptonica::leptonica"]
        if self.options.get_safe("with_libcurl", default=False):
            self.cpp_info.components["libtesseract"].requires.append("libcurl::libcurl")
        if self.options.get_safe("with_libarchive", default=True):
            self.cpp_info.components["libtesseract"].requires.append("libarchive::libarchive")
        if self.options.shared:
            self.cpp_info.components["libtesseract"].defines = ["TESS_IMPORTS"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtesseract"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libtesseract"].system_libs = ["ws2_32"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "Tesseract"
        self.cpp_info.names["cmake_find_package_multi"] = "Tesseract"
        self.cpp_info.components["libtesseract"].names["cmake_find_package"] = "libtesseract"
        self.cpp_info.components["libtesseract"].names["cmake_find_package_multi"] = "libtesseract"
        self.cpp_info.components["libtesseract"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libtesseract"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["libtesseract"].set_property("pkg_config_name", "tesseract")

    @property
    def _libname(self):
        suffix = ""
        if self.settings.os == "Windows":
            v = tools.Version(self.version)
            suffix += "{}{}".format(v.major, v.minor)
            if self.settings.build_type == "Debug":
                suffix += "d"
        return "tesseract" + suffix

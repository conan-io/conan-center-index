import os
import textwrap
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class TesseractConan(ConanFile):
    name = "tesseract"
    description = "Tesseract Open Source OCR Engine"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("ocr", "image", "multimedia", "graphics")
    license = "Apache-2.0"
    homepage = "https://github.com/tesseract-ocr/tesseract"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_auto_optimize": [True, False],
        "with_march_native": [True, False],
        "with_training": [True, False],
        "with_libcurl": [True, False],
        "with_libarchive": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_auto_optimize": False,
        "with_march_native": False,
        "with_training": False,
        "with_libcurl": True,
        "with_libarchive": True
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
            self.requires("libarchive/3.5.2")
        # libcurl is not required for 4.x
        if self.options.get_safe("with_libcurl", default=False):
            self.requires("libcurl/7.79.1")

    def validate(self):
        # Check compiler version
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        if tools.Version(self.version) >= "5.0.0":
            # 5.0.0 requires C++-17 compiler
            minimal_version = {
                "Visual Studio": "16",
                "gcc": "9",
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
            raise ConanInvalidConfiguration("{} requires a {} version >= {}".format(self.name, compiler, compiler_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = self._cmake = CMake(self)
        cmake.definitions["BUILD_TRAINING_TOOLS"] = self.options.with_training

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

        if tools.cross_building(self) and not tools.get_env("CMAKE_SYSTEM_PROCESSOR"):
            # FIXME: too specific and error prone, should be delegated to CMake helper
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = cmake_system_processor

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        # required for 5.0
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        # Official CMake imported target is:
        # - libtesseract if < 5.0.0
        # - Tesseract::libtesseract if >= 5.0.0 (not yet released)
        # We provide both targets
        self.cpp_info.names["cmake_find_package"] = "Tesseract"
        self.cpp_info.names["cmake_find_package_multi"] = "Tesseract"
        self.cpp_info.names["pkg_config"] = "tesseract"
        self.cpp_info.components["libtesseract"].names["cmake_find_package"] = "libtesseract"
        self.cpp_info.components["libtesseract"].names["cmake_find_package_multi"] = "libtesseract"
        self.cpp_info.components["libtesseract"].names["pkg_config"] = "tesseract"
        self.cpp_info.components["libtesseract"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["libtesseract"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libtesseract"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
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

    @property
    def _libname(self):
        suffix = ""
        if self.settings.os == "Windows":
            v = tools.Version(self.version)
            suffix += "{}{}".format(v.major, v.minor)
            if self.settings.build_type == "Debug":
                suffix += "d"
        return "tesseract" + suffix

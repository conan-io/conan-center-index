import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration


class TesseractConan(ConanFile):
    name = "tesseract"
    description = "Tesseract Open Source OCR Engine"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "ocr", "image", "multimedia", "graphics")
    license = "Apache-2.0"
    homepage = "https://github.com/tesseract-ocr/tesseract"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_auto_optimize": [True, False],
               "with_march_native": [True, False],
               "with_training": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_auto_optimize": False,
                       "with_march_native": False,
                       "with_training": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("leptonica/1.80.0")
        self.requires("libarchive/3.5.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_training:
            # do not enforce failure and allow user to build with system cairo, pango, fontconfig
            self.output.warn("*** Build with training is not yet supported, continue on your own")

        # Check compiler version
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = self._cmake = CMake(self)
        cmake.definitions["BUILD_TRAINING_TOOLS"] = self.options.with_training
        cmake.definitions["STATIC"] = not self.options.shared
        # Use CMake-based package build and dependency detection, not the pkg-config, cppan or SW
        cmake.definitions["CPPAN_BUILD"] = False
        cmake.definitions["SW_BUILD"] = False

        cmake.definitions["AUTO_OPTIMIZE"] = self.options.with_auto_optimize

        # Set Leptonica_DIR to ensure that find_package will be called in original CMake file
        cmake.definitions["Leptonica_DIR"] = self.deps_cpp_info["leptonica"].rootpath

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        if not self.options.with_march_native:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "if(COMPILER_SUPPORTS_MARCH_NATIVE)",
                "if(False)")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        # remove man pages
        tools.rmdir(os.path.join(self.package_folder, 'share', 'man'))
        # remove pkgconfig
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        # remove cmake
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))
        # required for 5.0
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Tesseract"
        self.cpp_info.names["cmake_find_package_multi"] = "Tesseract"

        self.cpp_info.components["libtesseract"].libs = tools.collect_libs(self)
        self.cpp_info.components["libtesseract"].requires = ["leptonica::leptonica", "libarchive::libarchive" ]

        self.cpp_info.components["libtesseract"].names["cmake_find_package"] = "libtesseract"
        self.cpp_info.components["libtesseract"].names["cmake_find_package_multi"] = "libtesseract"
        self.cpp_info.components["libtesseract"].names["pkg_config"] = "libtesseract"

        if self.settings.os == "Linux":
            self.cpp_info.components["libtesseract"].system_libs = ["pthread"]
        elif self.settings.compiler == "Visual Studio":
            self.cpp_info.components["libtesseract"].system_libs = ["ws2_32"]

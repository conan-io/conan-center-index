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
               "with_training": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_training": False}

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
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_training:
            # do not enforce failure and allow user to build with system cairo, pango, fontconfig
            self.output.warn("*** Build with training is not yet supported, continue on your own")

    def configure(self):
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        minimal_version = {
            "Visual Studio": "14",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "6"
        }

        if compiler in minimal_version and \
           compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a {} version >= {}" % (self.name, compiler, compiler_version))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = self._cmake = CMake(self)
        cmake.definitions["BUILD_TRAINING_TOOLS"] = self.options.with_training
        cmake.definitions["STATIC"] = not self.options.shared
        # Use CMake-based package build and dependency detection, not the pkg-config, cppan or SW
        cmake.definitions["CPPAN_BUILD"] = False
        cmake.definitions["SW_BUILD"] = False

        # avoid accidentally picking up system libarchive
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_LIBARCHIVE"] = True

        # Set Leptonica_DIR to ensure that find_package will be called in original CMake file
        cmake.definitions["Leptonica_DIR"] = self.deps_cpp_info["leptonica"].rootpath

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
        # remove man pages
        tools.rmdir(os.path.join(self.package_folder, 'share', 'man'))
        # remove pkgconfig
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        # remove cmake
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))
        # required for 5.0
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.compiler == "Visual Studio":
            if not self.options.shared:
                self.cpp_info.system_libs = ["ws2_32"]
        self.cpp_info.names["cmake_find_package"] = "Tesseract"
        self.cpp_info.names["cmake_find_package_multi"] = "Tesseract"

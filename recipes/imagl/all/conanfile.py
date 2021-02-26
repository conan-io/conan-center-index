from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.errors import ConanException
import os

required_conan_version = ">=1.32.0"


class ImaglConan(ConanFile):
    name = "imagl"
    license = "GPL-3.0-or-later"
    homepage = "https://github.com/Woazim/imaGL"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A lightweight library to load image for OpenGL application."
    topics = ("opengl", "texture", "image")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_png": [True, False], "with_jpeg": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_png": True, "with_jpeg": True}
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        minimum_versions = {
                "gcc": "9",
                "Visual Studio": "16.2",
                "clang": "10",
                "apple-clang": "11"
        }
        if tools.Version(self.version) <= "0.1.1" or tools.Version(self.version) == "0.2.0":
            minimum_versions["Visual Studio"] = "16.5"
        return minimum_versions

    @property
    def _supports_jpeg(self):
        return tools.Version(self.version) >= "0.2.0"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-v" + self.version, self._source_subfolder)

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 20)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]
        
        compiler_version = str(self.settings.compiler.version)
        if str(self.settings.compiler) == "Visual Studio" and str(self.settings.compiler.version).find(".") == -1 and int(str(self.settings.compiler.version)) >= 16:
            try:
                compiler_version = tools.vswhere(requires=["Microsoft.VisualStudio.Component.VC.Tools.x86.x64"],
                    version="[{}.0,{}.0)".format(str(self.settings.compiler.version), int(str(self.settings.compiler.version))+1), latest=True, property_="installationVersion")[0]["installationVersion"]
            except ConanException:
                raise ConanInvalidConfiguration("Your Visual Studio compiler seems not to be installed in a common way. It is not supported.")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("imagl requires C++20. Your compiler is unknown. Assuming it supports C++20.")
        elif lazy_lt_semver(compiler_version, minimum_version):
            raise ConanInvalidConfiguration("imagl requires some C++20 features, which your {} {} compiler does not support.".format(str(self.settings.compiler), compiler_version))
        else:
            print("Your compiler is {} {} and is compatible.".format(str(self.settings.compiler), compiler_version))
        #Special check for clang that can only be linked to libc++
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration("imagl requires some C++20 features, which are available in libc++ for clang compiler.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._supports_jpeg:
            del self.options.with_jpeg

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self._supports_jpeg and self.options.with_jpeg:
            self.requires("libjpeg/9d")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not self.settings.compiler.cppstd:
            self._cmake.definitions['CONAN_CMAKE_CXX_STANDARD'] = "20"
        self._cmake.definitions["STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["SUPPORT_PNG"] = self.options.with_png
        if self._supports_jpeg:
            self._cmake.definitions["SUPPORT_JPEG"] = self.options.with_jpeg
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        debug_suffix = "d" if self.settings.build_type == "Debug" else ""
        static_suffix = "" if self.options.shared else "s"
        self.cpp_info.libs = ["imaGL{}{}".format(debug_suffix, static_suffix)]
        if not self.options.shared:
            self.cpp_info.defines = ["IMAGL_STATIC=1"]


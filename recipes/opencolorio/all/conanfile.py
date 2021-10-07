from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class OpenColorIOConan(ConanFile):
    name = "opencolorio"
    description = "A color management framework for visual effects and animation."
    license = "BSD-3-Clause"
    homepage = "https://opencolorio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_sse": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse": True
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    topics = ("colors", "visual", "effects", "animation")

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
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.use_sse

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        # TODO: add GLUT (needed for ociodisplay tool)
        self.requires("lcms/2.12")
        self.requires("yaml-cpp/0.7.0")
        if tools.Version(self.version) < "2.1.0":
            self.requires("tinyxml/2.6.2")
        if tools.Version(self.version) >= "2.1.0":
            self.requires("pystring/1.1.3")
        self.requires("expat/2.4.1")
        self.requires("openexr/2.5.7")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        if tools.Version(self.version) >= "2.1.0":
            self._cmake.definitions["OCIO_BUILD_PYTHON"] = False
        else:
            self._cmake.definitions["OCIO_BUILD_SHARED"] = self.options.shared
            self._cmake.definitions["OCIO_BUILD_STATIC"] = not self.options.shared
            self._cmake.definitions["OCIO_BUILD_PYGLUE"] = False

            self._cmake.definitions["USE_EXTERNAL_YAML"] = True
            self._cmake.definitions["USE_EXTERNAL_TINYXML"] = True
            self._cmake.definitions["USE_EXTERNAL_LCMS"] = True

        self._cmake.definitions["OCIO_USE_SSE"] = self.options.get_safe("use_sse", False)

        # openexr 2.x provides Half library
        self._cmake.definitions["OCIO_USE_OPENEXR_HALF"] = True

        self._cmake.definitions["OCIO_BUILD_APPS"] = True
        self._cmake.definitions["OCIO_BUILD_DOCS"] = False
        self._cmake.definitions["OCIO_BUILD_TESTS"] = False
        self._cmake.definitions["OCIO_BUILD_GPU_TESTS"] = False
        self._cmake.definitions["OCIO_USE_BOOST_PTR"] = False

        # avoid downloading dependencies
        self._cmake.definitions["OCIO_INSTALL_EXT_PACKAGE"] = "NONE"

        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            # define any value because ifndef is used
            self._cmake.definitions["OpenColorIO_SKIP_IMPORTS"] = True

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        for module in ("expat", "lcms2", "pystring", "yaml-cpp", "Imath"):
            tools.remove_files_by_mask(os.path.join(self._source_subfolder, "share", "cmake", "modules"), "Find"+module+".cmake")

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        if not self.options.shared:
            self.copy("*", src=os.path.join(self.package_folder,
                      "lib", "static"), dst="lib")
            tools.rmdir(os.path.join(self.package_folder, "lib", "static"))

        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        # nop for 2.x
        tools.remove_files_by_mask(self.package_folder, "OpenColorIOConfig*.cmake")

        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenColorIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenColorIO"
        self.cpp_info.names["pkg_config"] = "OpenColorIO"

        self.cpp_info.libs = tools.collect_libs(self)

        if tools.Version(self.version) < "2.1.0":
            if not self.options.shared:
                self.cpp_info.defines.append("OpenColorIO_STATIC")

        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Foundation", "IOKit", "ColorSync", "CoreGraphics"])

        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            self.cpp_info.defines.append("OpenColorIO_SKIP_IMPORTS")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

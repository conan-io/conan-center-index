from conan.tools.microsoft import is_msvc
from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.45.0"


class OpenColorIOConan(ConanFile):
    name = "opencolorio"
    description = "A color management framework for visual effects and animation."
    license = "BSD-3-Clause"
    homepage = "https://opencolorio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("colors", "visual", "effects", "animation")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_sse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse": True,
    }

    generators = "cmake", "cmake_find_package"

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
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.use_sse

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("expat/2.4.8")
        self.requires("openexr/2.5.7")
        self.requires("yaml-cpp/0.7.0")
        if tools.scm.Version(self.version) < "2.0.0":
            self.requires("tinyxml/2.6.2")
        else:
            self.requires("pystring/1.1.3")
        # for tools only
        self.requires("lcms/2.13.1")
        # TODO: add GLUT (needed for ociodisplay tool)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        if tools.scm.Version(self.version) >= "2.1.0":
            cmake.definitions["OCIO_BUILD_PYTHON"] = False
        else:
            cmake.definitions["OCIO_BUILD_SHARED"] = self.options.shared
            cmake.definitions["OCIO_BUILD_STATIC"] = not self.options.shared
            cmake.definitions["OCIO_BUILD_PYGLUE"] = False

            cmake.definitions["USE_EXTERNAL_YAML"] = True
            cmake.definitions["USE_EXTERNAL_TINYXML"] = True
            cmake.definitions["USE_EXTERNAL_LCMS"] = True

        cmake.definitions["OCIO_USE_SSE"] = self.options.get_safe("use_sse", False)

        # openexr 2.x provides Half library
        cmake.definitions["OCIO_USE_OPENEXR_HALF"] = True

        cmake.definitions["OCIO_BUILD_APPS"] = True
        cmake.definitions["OCIO_BUILD_DOCS"] = False
        cmake.definitions["OCIO_BUILD_TESTS"] = False
        cmake.definitions["OCIO_BUILD_GPU_TESTS"] = False
        cmake.definitions["OCIO_USE_BOOST_PTR"] = False

        # avoid downloading dependencies
        cmake.definitions["OCIO_INSTALL_EXT_PACKAGE"] = "NONE"

        if is_msvc(self) and not self.options.shared:
            # define any value because ifndef is used
            cmake.definitions["OpenColorIO_SKIP_IMPORTS"] = True

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        for module in ("expat", "lcms2", "pystring", "yaml-cpp", "Imath"):
            tools.files.rm(self, os.path.join(self._source_subfolder, "share", "cmake", "modules"), "Find"+module+".cmake")

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
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "static"))

        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        # nop for 2.x
        tools.files.rm(self, self.package_folder, "OpenColorIOConfig*.cmake")

        tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.pdb")

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenColorIO")
        self.cpp_info.set_property("cmake_target_name", "OpenColorIO::OpenColorIO")
        self.cpp_info.set_property("pkg_config_name", "OpenColorIO")

        self.cpp_info.libs = ["OpenColorIO"]

        if tools.scm.Version(self.version) < "2.1.0":
            if not self.options.shared:
                self.cpp_info.defines.append("OpenColorIO_STATIC")

        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Foundation", "IOKit", "ColorSync", "CoreGraphics"])

        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines.append("OpenColorIO_SKIP_IMPORTS")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenColorIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenColorIO"
        self.cpp_info.names["pkg_config"] = "OpenColorIO"

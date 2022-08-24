from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class Exiv2Conan(ConanFile):
    name = "exiv2"
    description = "Exiv2 is a C++ library and a command-line utility " \
                  "to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata."
    license = "GPL-2.0"
    topics = ("image", "exif", "xmp")
    homepage = "https://www.exiv2.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_xmp": [False, "bundled", "external"],
        "with_curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_xmp": "bundled",
        "with_curl": False,
    }

    provides = []

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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
        if self.options.with_xmp == "bundled":
            # recipe has bundled xmp-toolkit-sdk of old version
            # avoid conflict with a future xmp recipe
            self.provides.append("xmp-toolkit-sdk")

    def requirements(self):
        self.requires("libiconv/1.16")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_xmp == "bundled":
            self.requires("expat/2.4.3")
        if self.options.with_curl:
            self.requires("libcurl/7.80.0")

    def validate(self):
        if self.options.with_xmp == "external":
            raise ConanInvalidConfiguration("adobe-xmp-toolkit is not available on cci (yet)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["EXIV2_BUILD_SAMPLES"] = False
        self._cmake.definitions["EXIV2_BUILD_EXIV2_COMMAND"] = False
        self._cmake.definitions["EXIV2_ENABLE_PNG"] = self.options.with_png
        self._cmake.definitions["EXIV2_ENABLE_XMP"] = self.options.with_xmp == "bundled"
        self._cmake.definitions["EXIV2_ENABLE_EXTERNAL_XMP"] = self.options.with_xmp == "external"
        # NLS is used only for tool which is not built
        self._cmake.definitions["EXIV2_ENABLE_NLS"] = False
        self._cmake.definitions["EXIV2_ENABLE_WEBREADY"] = self.options.with_curl
        self._cmake.definitions["EXIV2_ENABLE_CURL"] = self.options.with_curl
        self._cmake.definitions["EXIV2_ENABLE_SSH"] = False
        if self._is_msvc:
            self._cmake.definitions["EXIV2_ENABLE_DYNAMIC_RUNTIME"] = "MD" in msvc_runtime_flag(self)
        # set PIC manually because of object target exiv2_int
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        targets = {"exiv2lib": "exiv2::exiv2lib"}
        if self.options.with_xmp == "bundled":
            targets.update({"exiv2-xmp": "exiv2::exiv2-xmp"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets
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
        self.cpp_info.set_property("cmake_file_name", "exiv2")
        self.cpp_info.set_property("pkg_config_name", "exiv2")

        # component exiv2lib
        self.cpp_info.components["exiv2lib"].set_property("cmake_target_name", "exiv2lib")
        self.cpp_info.components["exiv2lib"].libs = ["exiv2"]
        self.cpp_info.components["exiv2lib"].requires = [ "libiconv::libiconv"]
        if self.options.with_png:
            self.cpp_info.components["exiv2lib"].requires.append("libpng::libpng")
        if self.options.with_curl:
            self.cpp_info.components["exiv2lib"].requires.append("libcurl::libcurl")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["exiv2lib"].system_libs.extend(["pthread"])
        if self.settings.os == "Windows":
            self.cpp_info.components["exiv2lib"].system_libs.extend(["psapi", "ws2_32"])
            self.cpp_info.components["exiv2lib"].defines.append("WIN32_LEAN_AND_MEAN")

        # component exiv2-xmp
        if self.options.with_xmp == "bundled":
            self.cpp_info.components["exiv2-xmp"].set_property("cmake_target_name", "exiv2-xmp")
            self.cpp_info.components["exiv2-xmp"].libs = ["exiv2-xmp"]
            self.cpp_info.components["exiv2-xmp"].requires = [ "expat::expat" ]
            self.cpp_info.components["exiv2lib"].requires.append("exiv2-xmp")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["exiv2lib"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["exiv2lib"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_xmp == "bundled":
            self.cpp_info.components["exiv2-xmp"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["exiv2-xmp"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

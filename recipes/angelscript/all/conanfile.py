from conan import ConanFile
from conan.tools.build import valid_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, get, export_conandata_patches, load, rmdir, save
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class AngelScriptConan(ConanFile):
    name = "angelscript"
    license = "Zlib"
    homepage = "http://www.angelcode.com/angelscript"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "An extremely flexible cross-platform scripting library designed to "
        "allow applications to extend their functionality through external scripts."
    )
    topics = ("angelcode", "embedded", "scripting", "language", "compiler", "interpreter")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [False, True],
        "fPIC": [False, True],
        "no_exceptions": [False, True],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_exceptions": False,
    }

    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        # Website blocks default user agent string.
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            headers={"User-Agent": "ConanCenter"},
            strip_root=True,
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["AS_NO_EXCEPTIONS"] = self.options.no_exceptions
        if not valid_min_cppstd(self, 11):
            tc.variables["CMAKE_CXX_STANDARD"] = 11
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "angelscript", "projects", "cmake"))
        cmake.build()

    def _extract_license(self):
        header = load(self, os.path.join(self.source_folder, "angelscript", "include", "angelscript.h"))
        return header[header.find("/*", 1) + 3 : header.find("*/", 1)]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Angelscript")
        self.cpp_info.set_property("cmake_target_name", "Angelscript::angelscript")
        postfix = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_angelscript"].libs = [f"angelscript{postfix}"]
        if self.settings.os in ("Linux", "FreeBSD", "SunOS"):
            self.cpp_info.components["_angelscript"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Angelscript"
        self.cpp_info.names["cmake_find_package_multi"] = "Angelscript"
        self.cpp_info.components["_angelscript"].names["cmake_find_package"] = "angelscript"
        self.cpp_info.components["_angelscript"].names["cmake_find_package_multi"] = "angelscript"
        self.cpp_info.components["_angelscript"].set_property("cmake_target_name", "Angelscript::angelscript")

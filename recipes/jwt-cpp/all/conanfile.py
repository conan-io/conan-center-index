from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class JwtCppConan(ConanFile):
    name = "jwt-cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Thalhammer/jwt-cpp"
    description = "A C++ JSON Web Token library for encoding/decoding"
    topics = ("json", "jwt", "jws", "jwe", "jwk", "jwks", "jose", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _supports_generic_json(self):
        return Version(self.version) >= "0.5.0"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("openssl/1.1.1s")
        if not self._supports_generic_json:
            self.requires("picojson/1.3.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        header_dir = os.path.join(self.source_folder, "include", "jwt-cpp")
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "jwt-cpp"), src=header_dir, keep_path=True)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder,"licenses"), src=self.source_folder)

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jwt-cpp")
        self.cpp_info.set_property("cmake_target_name", "jwt-cpp::jwt-cpp")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "jwt-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "jwt-cpp"

        if self._supports_generic_json:
            self.cpp_info.defines.append("JWT_DISABLE_PICOJSON")

        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

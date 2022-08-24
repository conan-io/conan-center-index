from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"

class JwtCppConan(ConanFile):
    name = "jwt-cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Thalhammer/jwt-cpp"
    description = "A C++ JSON Web Token library for encoding/decoding"
    topics = ("jwt-cpp", "json", "jwt", "jws", "jwe", "jwk", "jwks", "jose", "header-only")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _supports_generic_json(self):
        return tools.scm.Version(self, self.version) >= "0.5.0"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        self.requires("openssl/1.1.1q")
        if not self._supports_generic_json:
            self.requires("picojson/1.3.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        header_dir = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="jwt-cpp/**.h", dst="include", src=header_dir, keep_path=True)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jwt-cpp")
        self.cpp_info.set_property("cmake_target_name", "jwt-cpp::jwt-cpp")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "jwt-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "jwt-cpp"

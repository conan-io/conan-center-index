from conans import ConanFile, tools
import os


class JwtCppConan(ConanFile):
    name = "jwt-cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Thalhammer/jwt-cpp"
    description = "A C++ JSON Web Token library for encoding/decoding"
    topics = ("jwt-cpp", "json", "jwt", "header-only", "jose")
    exports_sources = ["patches/**"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("picojson/1.3.0")
        self.requires("openssl/1.1.1f")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def package(self):
        header_dir = os.path.join(self._source_subfolder, "include", "jwt-cpp")
        self.copy("jwt.h", dst="include", src=header_dir, keep_path=False)
        self.copy("base.h", dst="include", src=header_dir, keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

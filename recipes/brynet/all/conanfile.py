from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"


class BrynetConan(ConanFile):
    name = "brynet"
    description = "Header Only Cross platform high performance TCP network library using C++ 11."
    license = "MIT"
    topics = ("conan", "brynet", "networking", "tcp", "websocket")
    homepage = "https://github.com/IronsDu/brynet"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler"
    options = {
        "with_openssl": [True, False],
    }
    default_options = {
        "with_openssl": True,
    }

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        if self.options.with_openssl:
            self.cpp_info.defines.append("BRYNET_USE_OPENSSL")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

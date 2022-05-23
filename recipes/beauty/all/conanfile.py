import os
from conans import ConanFile, tools
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class BeautyConan(ConanFile):
    name = "beauty"
    homepage = "https://github.com/dfleury2/beauty"
    description = "HTTP Server above Boost.Beast"
    topics = ("http", "server", "boost.beast")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    requires = ("boost/[>1.70.0]@",
                "openssl/1.1.1o@")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15.7",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build(target="beauty")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("version.hpp", dst=os.path.join("include", "beauty"), src=os.path.join(self.build_folder, "src", "beauty"))
        self.copy("*.lib", src="lib", dst="lib", keep_path=False)
        self.copy("*.so*", src="lib", dst="lib", keep_path=False, symlinks=True)
        self.copy("*.a", src="lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["beauty"]
        self.cpp_info.requires = ["boost::headers", "openssl::openssl"]

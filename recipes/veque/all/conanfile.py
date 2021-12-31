import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class VequeConan(ConanFile):
    name = "veque"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Shmoopty/veque"
    description = "Fast C++ container combining the best features of std::vector and std::deque"
    topics = ("cpp17", "vector", "deque")
    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _supports_cpp17(self):
        supported_compilers = [("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = tools.Version(compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("C++17 support is required")

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)


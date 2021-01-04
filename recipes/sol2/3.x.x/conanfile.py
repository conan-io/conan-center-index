from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class Sol2Conan(ConanFile):
    name = "sol2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ThePhD/sol2"
    description = "C++17 Lua bindings"
    topics = ("conan", "lua", "c++", "bindings")
    settings = "compiler"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "clang": "6",
            "apple-clang": "10",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("sol2 requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("sol2 requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

    def requirements(self):
        self.requires("lua/5.3.5")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_info(self):
        if self.options["lua"].compile_as_cpp:
            self.cpp_info.defines.append("SOL_USING_CXX_LUA=1")

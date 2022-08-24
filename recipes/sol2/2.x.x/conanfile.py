from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration, ConanException
import os


class Sol2Conan(ConanFile):
    name = "sol2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ThePhD/sol2"
    description = "C++17 Lua bindings"
    topics = ("conan", "lua", "c++", "bindings")
    settings = "os", "compiler", "build_type", "arch"
    license = "MIT"
    requires = ["lua/5.3.5"]

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder
        )
        return self._cmake

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")
        compiler = str(self.settings.compiler)
        comp_version = tools.Version(self.settings.compiler.version)
        compilers = {"Visual Studio": "14", "gcc": "5",
                     "clang": "3.2", "apple-clang": "4.3"}
        min_version = compilers.get(compiler)
        if not min_version:
            self.output.warn(
                "sol2 recipe lacks information about the %s compiler support".format(compiler))
        elif comp_version < min_version:
            raise ConanInvalidConfiguration("sol2 requires C++14 or higher support standard."
                                            " {} {} is not supported."
                                            .format(compiler, comp_version))

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        # constains just # , "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        # constains just # , "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options["lua"].compile_as_cpp:
            self.cpp_info.defines.append("SOL_USING_CXX_LUA=1")

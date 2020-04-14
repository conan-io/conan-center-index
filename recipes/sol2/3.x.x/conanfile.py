from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration, ConanException
import os


class Sol2Conan(ConanFile):
    name = "sol2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ThePhD/sol2"
    description = "C++17 Lua bindings"
    topics = ("conan", "lua", "c++", "bindings")
    settings = "os", "compiler"
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


    def _has_support_for_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, tools.Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("sol2 requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        #there is a bug in cmake install in 3.0.3, so handel this
        if tools.Version(self.version) == "3.0.3":
            self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)
            self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "share")) # constains just # , "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "lib" )) # constains just # , "cmake"))

    def package_id(self):
        self.info.header_only()

    def package_info(self): 
        if self.options["lua"].compile_as_cpp :
            self.cpp_info.defines.append("SOL_USING_CXX_LUA=1")

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
    default_options = {"lua:compile_as_cpp": True}
    
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
        minimal_cpp_standard = "17"
        try:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        except ConanInvalidConfiguration:
            raise
        except ConanException:
            # FIXME: We need to handle the case when Conan doesn't know
            # about a user defined compiler's default standard version
            self.output.warn(
                "Unnable to determine the default standard version of the compiler")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
    # this is buggy in < 3.2.0, and it is less work to just copy the headers, 
    # because this is what install does. However, for future releases, leave this here    
#        cmake = self._configure_cmake()
#        cmake.install()
#        tools.rmdir(os.path.join(self.package_folder, "share")) # constains just # , "pkgconfig"))
#        tools.rmdir(os.path.join(self.package_folder, "lib" )) # constains just # , "cmake"))

        self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):        
        self.cpp_info.defines.append("SOL_USING_CXX_LUA=1")

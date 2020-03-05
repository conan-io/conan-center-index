from conans import ConanFile, CMake, tools


class LinenoisengConan(ConanFile):
    name = "linenoise-ng"
    license = "BSD"
    homepage = "https://github.com/arangodb/linenoise-ng"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("A small, portable GNU readline replacement for Linux,"
                   "Windows and MacOS which is capable of handling UTF-8 "
                   "characters.")
    topics = ("conan", "linenoise-ng", "linenoise", "readline")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True}
    generators = "cmake"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.replace_in_file(
            "linenoise-ng-1.0.1/CMakeLists.txt",
            "project(linenoise)",
            '''project(linenoise)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="linenoise-ng-1.0.1")
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src="linenoise-ng-1.0.1")
        self.copy("*.h", dst="include", src="linenoise-ng-1.0.1/include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

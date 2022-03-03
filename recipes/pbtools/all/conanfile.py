from conans import ConanFile, CMake, tools


class PbtoolsConan(ConanFile):
    name = "pbtools"
    description = "A Google Protocol Buffers C library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eerimoq/pbtools"
    license = "MIT"
    topics = ("protobuf", )
    settings = ("os", "compiler", "build_type", "arch")
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=f'pbtools-{self.version}/lib')
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=f'pbtools-{self.version}')

    def package_info(self):
        self.cpp_info.libs = ["pbtools"]

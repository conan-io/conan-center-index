from conans import ConanFile, CMake, tools
import platform, os


class BondConan(ConanFile):
    name = "bond"
    version = "9.0.0"
    license = "MIT License"
    author = "Lu Ye luye@microsoft.com"
    url = "https://github.com/microsoft/bond.git"
    description = "Bond is a cross-platform framework for working with schematized data. It supports cross-language de/serialization and powerful generic mechanisms for efficiently manipulating data. Bond is broadly used at Microsoft in high scale services."
    topics = ("bond", "microsoft")
    settings = "os", "compiler", "build_type", "arch"
    # options = {"shared": [False]}
    default_options = {"shared": False}
    build_requires = "boost/1.71.0@conan/stable"
    generators = "cmake"
    exports_sources = ["FindBond.cmake"]

    def source(self):
        self.run("git clone https://github.com/microsoft/bond.git")
        self.run("git checkout fe6f582ce4beb65644d9338536066e07d80a0289", cwd='bond')
        self.run("git submodule update --init --recursive", cwd='bond')
        tools.replace_in_file("bond/CMakeLists.txt",
                              "project (bond)",
                              '''project (bond)
message("BOOST_ROOT=$ENV{BOOST_ROOT}")''')

    def configure_cmake(self):
        if platform.system() == "Linux":
            self.run("curl -sSL https://get.haskellstack.org/ | sh", ignore_errors=True)
        cmake = CMake(self)
        cmake.definitions["BOND_ENABLE_GRPC"] = 'FALSE'
        cmake.configure(source_folder="bond")
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        # CMAKE_INSTALL_PREFIX is set to self.package_folder
        cmake.install()
        if platform.system() == 'Linux':
            self.run("chmod +rx *", cwd=f'{self.package_folder}/bin')
        self.copy("FindBond.cmake", ".", ".")

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libdirs = ['lib/bond']
        self.cpp_info.libs = ["bond"]


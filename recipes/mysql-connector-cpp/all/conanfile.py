from conans import ConanFile, CMake, tools


class MysqlConnectorCppConan(ConanFile):
    name = "mysql-connector-cpp"
    version = "8.0.27"
    license = "GPLv2"
    author = "Oracle"
    url = "https://dev.mysql.com/doc/connector-cpp/en/"
    description = "MySQL Connector/C++ is a MySQL database connector for C++."
    topics = ("mysql", "database", "connector", "c++")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    requires = "openssl/1.1.1k"

    def config_options(self):
        pass
        

    def source(self):
        self.run("git clone https://github.com/mysql/mysql-connector-cpp.git")
        self.run("cd mysql-connector-cpp && git checkout %s" % self.version)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="mysql-connector-cpp", build_folder="build")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="mysql-connector-cpp/include")
        if self.options.shared:
            self.copy("*.so*", dst="lib", keep_path=False)
            self.copy("*.dylib*", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["mysqlcppconn8"]


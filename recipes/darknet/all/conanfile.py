from conans import ConanFile, tools, AutoToolsBuildEnvironment


class DarknetConan(ConanFile):
    name = "darknet"
    version = "0.1"
    license = "YOLO"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pjreddie.com/darknet/"
    description = "Darknet is a neural network frameworks written in C"
    topics = ("darknet", "neural network", "deep learning")
    settings = "os", "compiler", "build_type", "arch", "arch_build"
    options = {
        "shared": [True, False],
        "OpenCV": [True, False],
    }
    default_options = {
        "shared": False,
        "OpenCV": False,
    }
    generators = "cmake"

    def activate_makefile(self, option):
        makefileName = option.upper()
        with tools.chdir("darknet-master"):
            if getattr(self.options, option) == True:
                print("option %s activated" % option)
                tools.replace_in_file('Makefile', makefileName + '=0', makefileName + '=1')

    def requirements(self):
        if self.options.OpenCV:
            self.requires("opencv/3.4.3@conan/stable")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def build(self):
        self.activate_makefile("OpenCV")
        with tools.chdir("darknet-master"):
            tools.replace_in_file('Makefile', "CFLAGS=", "CFLAGS+=${CPPFLAGS} ")
            tools.replace_in_file('Makefile', "LDFLAGS=", "LDFLAGS+=${LIBS} ")
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make()

    def package(self):
        self.copy("LICENSE", dst="licenses", src="darknet-master")
        self.copy("*.h", dst="include", src="darknet-master/include")
        if self.options.shared:
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.so", dst="lib", keep_path=False)
            self.copy("*.dylib", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["darknet"]
        if not self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.cxxflags = ["-pthread"]

    def configure(self):
        del self.settings.compiler.libcxx

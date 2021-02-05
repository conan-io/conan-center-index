import os
from conans import ConanFile, CMake, tools
from conans import AutoToolsBuildEnvironment

class ZmqppConan(ConanFile):
    name = "zmqpp"
    homepage = "https://github.com/zeromq/zmqpp"
    version = "4.2.0"
    license = "MPLv2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "This C++ binding for 0mq/zmq is a 'high-level' library that hides most of the c-style interface core 0mq provides."
    topics = ("conan", "zmq", "0mq", "ZeroMQ", "message-queue", "asynchronous")
    settings = "os", "compiler", "build_type", "arch"
    requires = "zeromq/4.3.3"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "make"

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "zmqpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        #self.run("git clone https://github.com/zeromq/zmqpp.git") # dir. will be zmqpp

        # zmpqq Makefile uses standard compiler variable name, useful for adding extra libs, so we rename it.
        tools.replace_in_file("source_subfolder/Makefile", "LIBRARY_PATH = $(SRC_PATH)/$(LIBRARY_DIR)",
                              "LIBRARY_PATH1 = $(SRC_PATH)/$(LIBRARY_DIR)\n$(info ENV==$(shell env))")
        tools.replace_in_file("source_subfolder/Makefile", "ALL_LIBRARY_OBJECTS := $(patsubst $(SRC_PATH)/%.cpp, $(OBJECT_PATH)/%.o, $(shell find $(LIBRARY_PATH) -iname '*.cpp'))",
                              "ALL_LIBRARY_OBJECTS := $(patsubst $(SRC_PATH)/%.cpp, $(OBJECT_PATH)/%.o, $(shell find $(LIBRARY_PATH1) -iname '*.cpp'))")
        tools.replace_in_file("source_subfolder/Makefile", "ALL_LIBRARY_INCLUDES := $(shell find $(LIBRARY_PATH) -iname '*.hpp')",
                              "ALL_LIBRARY_INCLUDES := $(shell find $(LIBRARY_PATH1) -iname '*.hpp')")

    def build(self):
        with tools.chdir("source_subfolder"):
            atools = AutoToolsBuildEnvironment(self)
            dir(atools)
            for property, value in vars(atools).items():
                print(property, ":", value)
            incpath=':'.join(atools.include_paths)
            libpath=':'.join(atools.library_paths)
            buildVars = atools.vars #add dependencies paths for building
            buildVars["CPLUS_INCLUDE_PATH"]=incpath
            buildVars["LIBRARY_PATH"]=libpath
            print("buildVars=")
            print(buildVars)
            atools.make(vars=buildVars)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include/zmqpp", src=self._source_subfolder + "/src/zmqpp")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["zmqpp"]


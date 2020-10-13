from subprocess import Popen, PIPE
from conans import ConanFile, CMake, tools

class PortmidiConan(ConanFile):
    name = "portmidi"
    version = "217"
    license = "MIT"
    author = "René Dudfield <renesd@gmail.com>"
    url = "https://sourceforge.net/projects/portmedia/"
    description = "Cross-platform library for real-time MIDI I/O"
    topics = ("midi", "audio")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"

    def source(self):
        tools.get('https://downloads.sourceforge.net/project/portmedia/portmidi/217/portmidi-src-217.zip',
                  sha256='08e9a892bd80bdb1115213fb72dc29a7bf2ff108b378180586aa65f3cfd42e0f')

        sdk_path = Popen(["xcrun", "--show-sdk-path"], stdout=PIPE).stdout.readlines()[0].decode('utf8')[:-1]

        tools.replace_in_file(
            "portmidi/pm_common/CMakeLists.txt",
            "set(CMAKE_OSX_SYSROOT /Developer/SDKs/MacOSX10.5.sdk CACHE",
            "set(CMAKE_OSX_SYSROOT %s CACHE" % sdk_path
        )
        tools.replace_in_file(
            "portmidi/CMakeLists.txt",
            "i386 ppc x86_64",
            "x86_64"
        )

    def build(self):
        # cmake = CMake(self)
        # print('cmake "%s" %s' % (self.source_folder, cmake.command_line))
        # print('cmake --build . %s' % cmake.build_config)

        self.run('make -f pm_mac/Makefile.osx', cwd='portmidi')

    def package(self):
        self.copy("*porttime.h", dst="include", keep_path=False)
        self.copy("*portmidi.h", dst="include", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["portmidi"]

import os
from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools


class CppcodecConan(ConanFile):
    name = "base64"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aklomp/base64"
    description = "Fast Base64 stream encoder/decoder"
    topics = ("base64", "codec")
    exports_sources = ["CMakeLists.txt", "cmake/*", "test/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            os.rename("CMakeLists.txt", os.path.join(self._source_subfolder, "CMakeLists.txt"))
            os.rename("cmake", os.path.join(self._source_subfolder, "cmake"))
            os.rename(os.path.join("test", "CMakeLists.txt"), os.path.join(self._source_subfolder, "test", "CMakeLists.txt"))
        else:
            s = "lib/libbase64.o: $(OBJS)"
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"), s, """
all: lib/libbase64.a
lib/libbase64.a: lib/libbase64.o
	$(AR) rc $@ $<
""" + s)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return cmake

    def _build_cmake(self):
        cmake = self._configure_cmake()
        cmake.build(target=self.name)

    def _build_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        if self.settings.arch == "x86" or self.settings.arch == "x86_64":
            extra_env = {
                "AVX2_CFLAGS": "-mavx2",
                "SSSE3_CFLAGS": "-mssse3",
                "SSE41_CFLAGS": "-msse4.1",
                "SSE42_CFLAGS": "-msse4.2",
                "AVX_CFLAGS": "-mavx"
            }
        else:
            # ARM-specific instructions can be enabled here
            extra_env = {}
        if self.settings.os == "Macos":
            extra_env["OBJCOPY"] = "llvm-objcopy"
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            extra_env["IS_MINGW"] = "1"
        with tools.environment_append(extra_env):
            with tools.chdir(self._source_subfolder):
                autotools.make()

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_cmake()
        else:
            self._build_autotools()

    def package(self):
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = [self.name]

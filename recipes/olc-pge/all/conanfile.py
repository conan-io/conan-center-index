from conans import ConanFile, tools


class oldPixelGameEngineConan(ConanFile):
    name = "olc-pge"
    homepage = "https://github.com/OneLoneCoder/olcPixelGameEngine"
    description = "The olcPixelGameEngine is a single-file prototyping and game-engine framework created in C++. It is cross platform, compiling on Windows via Visual Studio and Code::Blocks, and on Linux with a modern g++."
    topics = ("conan", "olc", "pge", "pixelengine", "pixelgameengine", "pgex",
              "game-development", "game-engine", "engine", "gamedev", "gaming", "graphics")
    license = "LicenseRef-LICENSE"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "image_loader": ['png', 'stb', 'default'],
    }
    default_options = {
        "image_loader": 'default',
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, 14)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("xorg/system")
        if self.options.image_loader == 'default':
            if self.settings.os != "Windows":
                self.requires("libpng/1.6.37")
        if self.options.image_loader == 'stb':
            self.requires("stb/20200203")
        elif self.options.image_loader == 'png':
            self.requires("libpng/1.6.37")

    def package(self):
        self.copy(pattern="LICENCE.md", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="olcPixelGameEngine.h",
                  dst="include", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include",
                  src=self._source_subfolder+"/Extensions")

    def package_info(self):
        self.cpp_info.libdirs = []
        if self.options.image_loader == "stb":
            self.cpp_info.defines = ["OLC_IMAGE_STB"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                "user32",
                "Shlwapi",
                "dwmapi",
            ])
            if self.options.image_loader == "default":
                self.cpp_info.system_libs.extend(["gdi32", "gdiplus", ])
            if self.options.image_loader == "png":
                self.cpp_info.defines = ["OLC_IMAGE_PNG"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "stdc++fs"]

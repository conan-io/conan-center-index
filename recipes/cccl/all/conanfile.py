from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class CcclConan(ConanFile):
    name = "cccl"
    description = "Unix cc compiler to Microsoft's cl compiler wrapper"
    topics = ("msvc", "visual studio", "wrapper", "gcc")
    homepage = "https://github.com/swig/cccl/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"
    options = {
        "muffle": [True, False],
        "verbose": [True, False],
    }
    default_options = {
        "muffle": True,
        "verbose": False,
    }
    settings = "compiler",

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("This recipe support only Visual Studio")
        del self.settings.compiler

    def package_id(self):
        del self.info.options.muffle
        del self.info.options.verbose

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

        cccl_path = os.path.join(self.source_folder, self._source_subfolder, "cccl")
        tools.files.replace_in_file(self, cccl_path,
                              "    --help)",
                              "    *.lib)\n"
                              "        linkopt+=(\"$lib\")"
                              "        ;;\n\n"
                              "    --help)")
        tools.files.replace_in_file(self, cccl_path,
                              "clopt+=(\"$lib\")",
                              "linkopt+=(\"$lib\")")
        tools.files.replace_in_file(self, cccl_path,
                              "    -L*)",
                              "    -LIBPATH:*)\n"
                              "        linkopt+=(\"$1\")\n"
                              "        ;;\n\n"
                              "    -L*)")

    def package(self):
        self.copy("cccl", src=os.path.join(self.source_folder, self._source_subfolder), dst="bin")
        self.copy("COPYING", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")

    def package_info(self):
        self.cpp_info.bindirs = ["bin", ]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        cccl_args = [
            "sh",
            os.path.join(self.package_folder, "bin", "cccl"),
        ]
        if self.options.muffle:
            cccl_args.append("--cccl-muffle")
        if self.options.verbose:
            cccl_args.append("--cccl-verbose")
        cccl = " ".join(cccl_args)

        self.output.info("Setting CC to '{}'".format(cccl))
        self.env_info.CC = cccl
        self.output.info("Setting CXX to '{}'".format(cccl))
        self.env_info.CXX = cccl
        self.output.info("Setting LD to '{}'".format(cccl))
        self.env_info.LD = cccl

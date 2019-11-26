from conans import ConanFile, CMake, tools

class Libtorch(ConanFile):
    name = "libtorch"
    version = "1.2.0"
    license = "BSD"
    homepage = "https://pytorch.org/"
    description = "PYTORCH C++ API"
    settings = {"os": ["Windows","Linux"],
        "build_type": ["Debug", "Release", "RelWithDebInfo"],
        "compiler": {"gcc": {"version": None,
                            "libcxx": ["libstdc++", "libstdc++11"]},
                    "Visual Studio": {"version": None},
                    }
        }

    options = {"cuda": ["9.2","10.0", "None"]}
    default_options = {"cuda": "None"}

    generators = "cmake"
    url_base = "https://download.pytorch.org/libtorch/"


    def getGPU(self):
        if(self.options.cuda == "9.2"):
            return "cu92/"
        if(self.options.cuda == "10.0"):
            return "cu100/"
        else:
            return "cpu/"

    def getOS(self):
        if(self.settings.os == "Windows"):
            if(self.settings.build_type == "Debug"):
                return "libtorch-win-shared-with-deps-debug-"
            return "libtorch-win-shared-with-deps-"
        if(self.settings.os == "Linux"):
            if(self.settings.compiler.libcxx == "libstdc++11"):
                return "libtorch-cxx11-abi-shared-with-deps-"
            return "libtorch-shared-with-deps-"
    
    def source(self):
        url = self.url_base + self.getGPU() + self.getOS() + self.version + ".zip"
        tools.get(url)

    def package(self):
        self.copy("*", src="libtorch/")

    def package_info(self):
        self.cpp_info.libs = ['torch', 'caffe2', 'c10', 'pthread']
        self.cpp_info.includedirs = ['include', 'include/torch/csrc/api/include']
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.libdirs = ['lib']
        if self.options.cuda != 'None':
            self.cpp_info.libs.extend(
                ['cuda', 'nvrtc', 'nvToolsExt', 'cudart', 'caffe2_gpu',
                 'c10_cuda', 'cufft', 'curand', 'cudnn', 'culibos', 'cublas'])


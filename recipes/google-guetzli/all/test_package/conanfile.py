import os

from conans import ConanFile, tools


class GoogleguetzliTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
   
    
    def test(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bees_path  = os.path.join(dir_path, "bees.png")
        print("{}".format(dir_path))
        if not tools.cross_building(self.settings):
            app = "guetzli"
            if self.settings.os == "Windows":
                app += ".exe"
            self.run("{} --quality 84 {} bees.jpg".format(app,bees_path), run_environment=True)
            

   
    

    

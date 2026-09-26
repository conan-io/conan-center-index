#include <iostream>
#include <sgltk/sgltk.h>

int main(void) {
    sgltk::App::init();
    sgltk::Window win("System info", 1200, 800, 100, 100, SDL_WINDOW_HIDDEN);
    std::cout<<"System info"<<std::endl<<std::endl;
    std::cout<<"OS: "<<sgltk::App::sys_info.platform_name<<std::endl;
    std::cout<<"CPU Cores: "<<sgltk::App::sys_info.num_logical_cores<<std::endl;
    std::cout<<"RAM: "<<sgltk::App::sys_info.system_ram<<"MB"<<std::endl;
    std::cout<<"Highest supported OpenGL version: "<<win.gl_maj<<"."<<win.gl_min<<std::endl;
    std::cout<<"Number of displays: "<<sgltk::App::sys_info.num_displays<<std::endl;

    return 0;
}

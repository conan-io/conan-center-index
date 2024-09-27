#include <cstdlib>
#include <iostream>
#include <thread>
#include <filesystem>
#include <fstream>
#include "efsw/efsw.hpp"


class UpdateListener : public efsw::FileWatchListener {
  public:
    void handleFileAction( efsw::WatchID watchid, const std::string& dir,
                           const std::string& filename, efsw::Action action,
                           std::string oldFilename ) override {
        switch ( action ) {
            case efsw::Actions::Add:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Added" << std::endl;
                break;
            case efsw::Actions::Delete:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Delete" << std::endl;
                break;
            case efsw::Actions::Modified:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Modified" << std::endl;
                break;
            case efsw::Actions::Moved:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Moved from (" << oldFilename << ")" << std::endl;
                break;
            default:
                std::cout << "Should never happen!" << std::endl;
        }
    }
};

int main(void) {
    using namespace std::chrono_literals;
    
    efsw::FileWatcher* fileWatcher = new efsw::FileWatcher();
    UpdateListener* listener = new UpdateListener();

    efsw::WatchID watchID = fileWatcher->addWatch( ".", listener, false );

    fileWatcher->watch();

    std::this_thread::sleep_for(100ms);

    const std::filesystem::path file = "./__test_file__.txt";
    {
        std::ofstream output(file);
    }
    std::filesystem::remove(file);

    fileWatcher->removeWatch( watchID );

    delete fileWatcher;
    delete listener;

    return EXIT_SUCCESS;
}

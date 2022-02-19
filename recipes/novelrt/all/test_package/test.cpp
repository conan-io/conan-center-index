#include <NovelRT.h>
#include <iostream>

int main()
{
    NovelRT::LoggingService logger = NovelRT::LoggingService();
    logger.setLogLevel(NovelRT::LogLevel::Info);
    
    std::filesystem::path finalPath = NovelRT::Utilities::Misc::getExecutableDirPath();
    logger.logInfoLine(finalPath.string());
    std::cout << "I'm heppeh, goodnite :)" << std::endl;
    return 0;
}

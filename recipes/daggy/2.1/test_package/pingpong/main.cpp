/*
MIT License

Copyright (c) 2021 synacker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include "Precompiled.h"

int main(int argc, char** argv)
{
    QCoreApplication app(argc, argv);

    const QCommandLineOption count_argument({"c", "count"}, "Count operations", "count");

    QCommandLineParser command_line_parser;
    command_line_parser.addOption(count_argument);
    command_line_parser.addHelpOption();
    command_line_parser.addVersionOption();

    command_line_parser.process(app);

    std::uint64_t count = std::numeric_limits<uint64_t>().max();

    if (command_line_parser.isSet(count_argument)) {
        bool ok = false;
        count = command_line_parser.value(count_argument).toULongLong(&ok);
        if (!ok)
            command_line_parser.showHelp(-1);
    }

    QTimer timer;
    std::uint64_t iteration = 0;
    timer.callOnTimeout([&](){
        if (iteration == count)
        {
            qApp->quit();
        }
        else
        {
            iteration++;
            std::cout << "Ping and Pong " << iteration << std::endl;
        }

    });
    timer.start(1000);

    return app.exec();
}

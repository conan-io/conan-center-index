/*
  This file is part of KDBindings.

  SPDX-FileCopyrightText: 2021-2022 Klarälvdalens Datakonsult AB, a KDAB Group company <info@kdab.com>
  Author: Leon Matthes <leon.matthes@kdab.com>

  SPDX-License-Identifier: MIT

  Contact KDAB at <info@kdab.com> for commercial licensing options.
*/

#include <ios>
#include <kdbindings/signal.h>

#include <iostream>
#include <string>

using namespace KDBindings;

void display()
{
    std::cout << "Hello World!" << std::endl;
}

void displayLabelled(const std::string &label, int value)
{
    std::cout << label << ": " << value << std::endl;
}

class SignalHandler
{
public:
    bool received = 0;

    void receive()
    {
        received = true;
    }
};

int main()
{
    Signal<int> signal;

    // Signal::connect allows connecting functions that take too few arguments.
    signal.connect(display);

    // As well as functions with too many arguments, as long as default values are provided.
    signal.connect(displayLabelled, "Emitted value");

    // This is very useful to connect member functions, where the first implicit argument
    // is a pointer to the "this" object.
    SignalHandler handler;
    signal.connect(&SignalHandler::receive, &handler);

    // This will print "Hello World!" and "Emitted value: 5" in an unspecified order.
    // It will also set handler.received to true
    signal.emit(5);

    std::cout << std::boolalpha << handler.received << std::endl;

    return 0;
}

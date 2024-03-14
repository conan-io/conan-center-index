// Copyright (C) 2019 Julian Sherollari <jdotsh@gmail.com>
// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#include <QDebug>
#include <QFile>
#include <QFileInfo>
#include <QGuiApplication>
#include <QIcon>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QTimer>
#include <QVariantMap>
#include <QtCore/qobjectdefs.h>

using namespace Qt::StringLiterals;

#include <SDL2/SDL.h>

#include "main.moc"

int main(int argc, char *argv[])
{
    // Instruct SDL to report events even when no window has focus
    SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");

    // Initialize SDL
    auto ret = SDL_Init(SDL_INIT_GAMECONTROLLER);
    if (ret < 0)
    {
        throw std::runtime_error(std::string("Failed to initialize SDL: ") +
                                 std::string(SDL_GetError()));
    }

    SDL_Event sdl_event;

    QGuiApplication app(argc, argv);

    app.setWindowIcon(QIcon(":/svg/lightbulb.svg"));

    // Periodically check SDL for joystick events
    QTimer *sdl_timer = new QTimer();
    QObject::connect(sdl_timer, &QTimer::timeout, [&]() {
        if (SDL_PollEvent(&sdl_event))
        {
            switch (sdl_event.type)
            {
            case SDL_JOYDEVICEADDED:
            {
                qInfo() << "Joystick connected";
                break;
            }

            case SDL_JOYDEVICEREMOVED:
            {
                qInfo() << "Joystick disconnected";
                break;
            }
            default:
            {
                break;
            }
            }
        }
    });
    sdl_timer->start(10);


    QQmlApplicationEngine engine;
    QUrl absoluteFilePath = argc > 1
                                ? QUrl(QStringLiteral("file://") +
                                       QFileInfo(argv[1]).absoluteFilePath())
                                : QUrl();
    engine.rootContext()->setContextProperty(
        "dataPath",
        QUrl(QStringLiteral("file://") + qPrintable(QT_STRINGIFY(SRC_PATH)) +
             QStringLiteral("/data")));

    engine.load(QUrl(QStringLiteral("qrc:/main.qml")));

    if (engine.rootObjects().isEmpty())
        return -1;

    auto appret = app.exec();

    sdl_timer->stop();
    delete sdl_timer;

    return appret;
}

// SPDX-FileCopyrightText: 2021 Daniel Vrátil <dvratil@kde.org>
//
// SPDX-License-Identifier: MIT

#include "qcorofuture.h"

#include <QCoreApplication>
#include <QTimer>
#include <QtConcurrent>

#include <iostream>
#include <random>

QCoro::Task<> startTask() {
    const auto data = co_await QtConcurrent::run([]() {
        QVector<std::uint64_t> data;
        std::random_device rd{};
        std::mt19937 gen{rd()};
        data.reserve(10'000'000);
        for (int i = 0; i < 10'000'000; ++i) {
            data.push_back(gen());
        }
        return data;
    });

    std::cout << "Generated " << data.size() << " random numbers" << std::endl;

    const auto sum = co_await QtConcurrent::filteredReduced<std::uint64_t>(
        data, [](const auto &) { return true; },
        [](std::uint64_t &interm, std::uint64_t val) { interm += val; },
        QtConcurrent::UnorderedReduce);

    std::cout << "Calculated result: " << sum << std::endl;
    qApp->quit();
}

int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    QTimer::singleShot(0, startTask);
    return app.exec();
}

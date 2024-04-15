// https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/v7.7.0/Mongoose/Demo/demo.cpp

/**
 * demo.cpp
 * Runs a variety of computations on several input matrices and outputs
 * the results. Does not take any input. This application can be used to
 * test that compilation was successful and that everything is working
 * properly.
 *
 * Mongoose, Copyright (c) 2018, All Rights Reserved.
 *   Nuri Yeralan, Microsoft Research
 *   Scott Kolodziej, Texas A&M University
 *   Tim Davis, Texas A&M University
 *   William Hager, University of Florida.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 */

#include "Mongoose.hpp"
#include <ctime>
#include <iostream>
#include <iomanip>
#include <cmath>

using namespace Mongoose;
using namespace std;

int main(int argn, const char **argv)
{
    if (argn != 2)
    {
        cout << "Usage: " << argv[0] << " <matrix path>" << endl;
        return EXIT_FAILURE;
    }

    std::string demo_file = argv[1];

    cout << "Mongoose Graph Partitioning Library, Version " << mongoose_version() << endl;

    cout << "Computing an edge cut for " << demo_file << "..." << endl;

    double trial_start = SUITESPARSE_TIME;
    EdgeCut_Options *options = EdgeCut_Options::create();
    if (!options) return EXIT_FAILURE; // Return an error if we failed.

    options->matching_strategy = HEMSRdeg;
    options->initial_cut_type = InitialEdgeCut_QP;

    Graph *graph = read_graph(demo_file);
    if (!graph)
    {
        return EXIT_FAILURE;
    }

    EdgeCut *result = edge_cut(graph, options);

    cout << "Cut Cost:       " << setprecision(2) << result->cut_cost << endl;
    if (result->imbalance < 1e-12)
    {
        // imbalance is zero; this is just a roundoff epsilon in the statistic
        cout << "Cut Imbalance:  zero (a perfect balance)" << endl;
    }
    else
    {
        cout << "Cut Imbalance:  " << setprecision(2) << 100*(result->imbalance) << "%" << endl;
    }

    options->~EdgeCut_Options();
    graph->~Graph();
    result->~EdgeCut();

    return EXIT_SUCCESS;
}

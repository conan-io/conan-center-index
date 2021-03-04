/**
 * Copyright (C) 2020, 2021 Alexis LE GOADEC.
 * 
 * This file is part of the Graphthewy project which is licensed under
 * the European Union Public License v1.2.
 * 
 * If a copy of the EUPL v1.2 was not distributed with this software,
 * you can obtain one at : https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

#include <graphthewy/GraphthewyModel.hpp>
#include <graphthewy/GraphthewyCycle.hpp>

#include <string>


/*************************************
 * Macro for graph instance
 * ***********************************/
#define GRAPH_TEMPTYPE                   int
#define GRAPH_CREATE(graph_name)         graphthewy::UndirectedGraph<GRAPH_TEMPTYPE> graph_name;
#define GRAPH_CYCLE(gc_name, graph_name) graphthewy::GraphCycle<graphthewy::UndirectedGraph, GRAPH_TEMPTYPE> gc_name(graph_name);
/*************************************/


int main(int argc, char** arvg)
{
    GRAPH_CREATE(g)
    g.addVertex(1);
    g.addVertex(2);
    g.addVertex(3);
    g.link(1, 2);
    g.link(2, 3);
    g.link(3, 1);

    GRAPH_CYCLE(gc, g)

    return (gc.hasCycle() == true ? 0 : -1);
}

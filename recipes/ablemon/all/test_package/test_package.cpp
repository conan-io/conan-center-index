/* -*- mode: C++; indent-tabs-mode: nil; -*-
 *
 * This file is a part of LEMON, a generic C++ optimization library.
 *
 * Copyright (C) 2003-2013
 * Egervary Jeno Kombinatorikus Optimalizalasi Kutatocsoport
 * (Egervary Research Group on Combinatorial Optimization, EGRES).
 *
 * Permission to use, modify and distribute this software is granted
 * provided that this copyright notice appears in all copies. For
 * precise terms see the accompanying LICENSE file.
 *
 * This software is provided "AS IS" with no warranty of any kind,
 * express or implied, and with no claim as to its suitability for any
 * purpose.
 *
 */

// A program built against an installed LEMON: it uses a header-only
// algorithm and a function of the library (the parser of the arguments),
// so that it needs both the include directory and the library.

#include <iostream>
#include <lemon/arg_parser.h>
#include <lemon/network_simplex.h>
#include <lemon/smart_graph.h>

int main( int argc , char * argv[] )
{
 lemon::ArgParser ap( argc , argv );
 ap.run();

 lemon::SmartDigraph g;
 lemon::SmartDigraph::Node s = g.addNode() , t = g.addNode();
 lemon::SmartDigraph::Arc a = g.addArc( s , t );
 lemon::SmartDigraph::ArcMap< int > cost( g , 2 ) , cap( g , 5 );
 lemon::SmartDigraph::NodeMap< int > supply( g , 0 );
 supply[ s ] = 3;
 supply[ t ] = -3;

 lemon::NetworkSimplex< lemon::SmartDigraph > ns( g );
 ns.costMap( cost ).upperMap( cap ).supplyMap( supply );
 if( ns.run() != ns.OPTIMAL || ns.totalCost() != 6 || ns.flow( a ) != 3 ) {
  std::cerr << "wrong result" << std::endl;
  return( 1 );
  }
 std::cout << "ok" << std::endl;
 return( 0 );
 }

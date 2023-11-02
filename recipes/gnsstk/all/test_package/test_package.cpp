// https://github.com/SGL-UT/gnsstk/blob/v14.0.0/examples/Rinex3ObsStream_example_1.cpp

//==============================================================================
//
//  This file is part of GNSSTk, the ARL:UT GNSS Toolkit.
//
//  The GNSSTk is free software; you can redistribute it and/or modify
//  it under the terms of the GNU Lesser General Public License as published
//  by the Free Software Foundation; either version 3.0 of the License, or
//  any later version.
//
//  The GNSSTk is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Lesser General Public License for more details.
//
//  You should have received a copy of the GNU Lesser General Public
//  License along with GNSSTk; if not, write to the Free Software Foundation,
//  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110, USA
//
//  This software was developed by Applied Research Laboratories at the
//  University of Texas at Austin.
//  Copyright 2004-2022, The Board of Regents of The University of Texas System
//
//==============================================================================

//==============================================================================
//
//  This software was developed by Applied Research Laboratories at the
//  University of Texas at Austin, under contract to an agency or agencies
//  within the U.S. Department of Defense. The U.S. Government retains all
//  rights to use, duplicate, distribute, disclose, or release this software.
//
//  Pursuant to DoD Directive 523024
//
//  DISTRIBUTION STATEMENT A: This software has been approved for public
//                            release, distribution is unlimited.
//
//==============================================================================

/** @file Rinex3ObsStream_example_1.cpp implements an extremely basic
 * example of using Rinex3ObsStream for input and output where the
 * input data is copied to the output with unnecessary processing. */

#include <iostream>
#include <iomanip>

#include "Rinex3ObsBase.hpp"
#include "Rinex3ObsHeader.hpp"
#include "Rinex3ObsData.hpp"
#include "Rinex3ObsStream.hpp"

using namespace std;
using namespace gnsstk;

int main()
{
   // Create the input file stream
   Rinex3ObsStream rin("bahr1620.04o");

   // Create the output file stream
   Rinex3ObsStream rout("bahr1620.04o.new", ios::out|ios::trunc);

   // Read the RINEX header
   Rinex3ObsHeader head;    //RINEX header object
   rin >> head;
   rout.header = rin.header;
   rout << rout.header;

   // Loop over all data epochs
   Rinex3ObsData data;   //RINEX data object
   while (rin >> data)
   {
      rout << data;
   }

   return 0;
}

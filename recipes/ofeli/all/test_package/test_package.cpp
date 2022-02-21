/*==============================================================================

                                    O  F  E  L  I

                            Object  Finite  Element  Library

  ==============================================================================

   Copyright (C) 1998 - 2015 Rachid Touzani
 
   This file is part of OFELI.

   OFELI is free software: you can redistribute it and/or modify
   it under the terms of the GNU Lesser General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   OFELI is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public License
   along with OFELI. If not, see <http://www.gnu.org/licenses/>.

  ==============================================================================

              An example of a Finite Element Code using OFELI

            Solution of a 1-D Elliptic problem using P1 Finite elements

  ==============================================================================*/

#include "OFELI.h"
using namespace OFELI;

int main(int argc, char *argv[])
{
   double L=1;
   int N=10;

/// Read and output mesh data
   banner();
   if (argc>1)
      N = atoi(argv[1]);
   Mesh ms(L,N);
   int NbN = N+1;

// Declare problem data (matrix, rhs, boundary conditions, body forces)
   TrMatrix<double> A(NbN);
   Vect<double> b(ms);
   b.set("16*pi*pi*sin(4*pi*x)");

// Build matrix and R.H.S.
   double h = L/double(N);
   b *= h;
   for (int i=2; i<NbN; i++) {
      A(i,i  ) =  2./h;
      A(i,i+1) = -1./h;
      A(i,i-1) = -1./h;
   }

// Impose boundary conditions
   A(1,1) = 1.; A(1,2) = 0.; b(1) = 0;
   A(NbN,NbN) = 1.; A(NbN-1,NbN) = 0.; b(NbN) = 0;

// Solve the linear system of equations
   A.solve(b);

// Output solution and error
   cout << "\nSolution:\n" << b;
   Vect<double> sol(ms);
   sol.set("sin(4*pi*x)");
   cout << "Error = " << (b-sol).getNormMax() << endl;
   return 0;
}

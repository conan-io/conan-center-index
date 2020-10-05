/* File : example.i */
%module example

%inline %{
extern int    gcd(int u, int v);
extern double foo;
%}

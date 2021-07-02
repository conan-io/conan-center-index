%module PackageTest

%inline %{
extern int    gcd(int u, int v);
extern double foo;
%}

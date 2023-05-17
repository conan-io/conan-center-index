#include <cstdlib>
#include <tao/operators.hpp>

class X
   : tao::operators::ordered_field< X >,
     tao::operators::modable< X >,
     tao::operators::ordered_field< X, int >,
     tao::operators::modable< X, int >
{
public:
   explicit X( const int v ) noexcept
      : v_( v )
   {
   }

   X( const X& ) = default;
   X( X&& ) = default;

   ~X() = default;

   X& operator=( const X& ) = delete;
   X& operator=( X&& ) = delete;

   X& operator+=( const X& x ) noexcept
   {
      v_ += x.v_;
      return *this;
   }

   X& operator-=( const X& x )
   {
      v_ -= x.v_;
      return *this;
   }

   X& operator*=( const X& x )
   {
      v_ *= x.v_;
      return *this;
   }

   X& operator/=( const X& x )
   {
      v_ /= x.v_;
      return *this;
   }

   X& operator%=( const X& x )
   {
      v_ %= x.v_;
      return *this;
   }

   X& operator+=( const int v )
   {
      v_ += v;
      return *this;
   }

   X& operator-=( const int v )
   {
      v_ -= v;
      return *this;
   }

   X& operator*=( const int v )
   {
      v_ *= v;
      return *this;
   }

   X& operator/=( const int v )
   {
      v_ /= v;
      return *this;
   }

   X& operator%=( const int v )
   {
      v_ %= v;
      return *this;
   }

   int v_;  // NOLINT
};

bool operator==( const X& lhs, const X& rhs )
{
   return lhs.v_ == rhs.v_;
}

int main()
{
    X x1( 1 );
    X x2( 2 );

    if (x1 == x2) {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

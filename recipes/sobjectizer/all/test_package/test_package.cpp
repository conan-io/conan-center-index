#include <iostream>

#include <so_5/all.hpp>

class a_hello_t final : public so_5::agent_t
{
  public:
    using so_5::agent_t::agent_t;

    // A reaction to start of work in SObjectizer.
    void so_evt_start() override
    {
      std::cout << "Hello, world! This is SObjectizer v.5 ("
          << SO_5_VERSION << ")" << std::endl;

      // Shutting down SObjectizer.
      so_environment().stop();
    }

    // A reaction to finish of work in SObjectizer.
    void so_evt_finish() override
    {
      std::cout << "Bye! This was SObjectizer v.5." << std::endl;
    }
};

int main()
{
  try
  {
    so_5::launch(
      []( so_5::environment_t & env ) {
        env.register_agent_as_coop( env.make_agent< a_hello_t >() );
      } );
  }
  catch( const std::exception & ex )
  {
    std::cerr << "Error: " << ex.what() << std::endl;
    return 1;
  }

  return 0;
}

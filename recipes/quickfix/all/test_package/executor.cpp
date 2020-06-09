#include "config.h"

#include "quickfix/FileStore.h"
#include "quickfix/Application.h"
#include "quickfix/SocketAcceptor.h"
#ifdef HAVE_SSL
  #include "quickfix/ThreadedSSLSocketAcceptor.h"
  #include "quickfix/SSLSocketAcceptor.h"
#endif
#include "quickfix/Log.h"
#include "quickfix/SessionSettings.h"

class Application
    : public FIX::Application
{
public:
  // Application overloads
  void onCreate( const FIX::SessionID& );
  void onLogon( const FIX::SessionID& sessionID );
  void onLogout( const FIX::SessionID& sessionID );
  void toAdmin( FIX::Message&, const FIX::SessionID& );
  void toApp( FIX::Message&, const FIX::SessionID& )
  EXCEPT( FIX::DoNotSend );
  void fromAdmin( const FIX::Message&, const FIX::SessionID& )
  EXCEPT( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon );
  void fromApp( const FIX::Message& message, const FIX::SessionID& sessionID )
  EXCEPT( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::UnsupportedMessageType );
};

void Application::onCreate( const FIX::SessionID& sessionID ) {}
void Application::onLogon( const FIX::SessionID& sessionID ) {}
void Application::onLogout( const FIX::SessionID& sessionID ) {}
void Application::toAdmin( FIX::Message& message,
                           const FIX::SessionID& sessionID ) {}
void Application::toApp( FIX::Message& message,
                         const FIX::SessionID& sessionID )
EXCEPT( FIX::DoNotSend ) {}

void Application::fromAdmin( const FIX::Message& message,
                             const FIX::SessionID& sessionID )
EXCEPT( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon ) {}

void Application::fromApp( const FIX::Message& message,
                           const FIX::SessionID& sessionID )
EXCEPT( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::UnsupportedMessageType )
{ }

int main( int argc, char** argv )
{
  FIX::Acceptor * acceptor = 0;
  try
  {
    FIX::SessionSettings settings( "" );

    Application application;
    FIX::FileStoreFactory storeFactory( settings );
    FIX::ScreenLogFactory logFactory( settings );

#ifdef HAVE_SSL
    acceptor = new FIX::ThreadedSSLSocketAcceptor ( application, storeFactory, settings, logFactory );
    acceptor = new FIX::SSLSocketAcceptor ( application, storeFactory, settings, logFactory );
#endif
    acceptor = new FIX::SocketAcceptor ( application, storeFactory, settings, logFactory );

    acceptor->start();
    acceptor->stop();
  }
  catch( std::exception & )
  {
    delete acceptor;
  }

  return 0;
}

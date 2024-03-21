#include "MockNetworkAccessManager.hpp"

int main(void) {
    MockNetworkAccess::Manager< QNetworkAccessManager > mnam;

    mnam.whenGet( QUrl( "http://example.com/hello" ) )
        .has( MockNetworkAccess::Predicates::HeaderMatching( QNetworkRequest::UserAgentHeader,
                    QRegularExpression( ".*MyNetworkClient/.*" ) ) )
        .reply().withBody( QJsonDocument::fromJson( "{\"hello\":\"world\"}" ) );

    return 0;
}

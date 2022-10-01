// #include <cstdint>
// #include <iostream>
// #include <vector>
// #include <bsoncxx/json.hpp>
// #include <mongocxx/client.hpp>
// #include <mongocxx/stdx.hpp>
// #include <mongocxx/uri.hpp>
// #include <mongocxx/instance.hpp>
// #include <bsoncxx/builder/stream/helpers.hpp>
// #include <bsoncxx/builder/stream/document.hpp>
// #include <bsoncxx/builder/stream/array.hpp>
#include "./libs/crow_all.h"


// using bsoncxx::builder::stream::close_array;
// using bsoncxx::builder::stream::close_document;
// using bsoncxx::builder::stream::document;
// using bsoncxx::builder::stream::finalize;
// using bsoncxx::builder::stream::open_array;
// using bsoncxx::builder::stream::open_document;
// using namespace std;
// using namespace crow;
// using namespace mongocxx;

// instance inst{};
// const auto ur = uri{ "mongodb+srv://primitt:1016@primittdb.mvkeq.mongodb.net/" };
// const auto dbconn = client{ ur };
// const auto datadb = dbconn["LS"];
// const auto coll = datadb["LS-SCORE"];

int main(){
    // query everything from ls-score
    SimpleApp app;
    CROW_ROUTE(app, "/")
    ([](){
        return "Hello World!";
    });

}
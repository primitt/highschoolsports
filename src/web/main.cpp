#include <cstdint>
#include <iostream>
#include <vector>
#include <bsoncxx/json.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/stdx.hpp>
#include <mongocxx/uri.hpp>
#include <mongocxx/instance.hpp>
#include <bsoncxx/builder/stream/helpers.hpp>
#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/builder/stream/array.hpp>
#include "libs/crow_all.h"


using bsoncxx::builder::stream::close_array;
using bsoncxx::builder::stream::close_document;
using bsoncxx::builder::stream::document;
using bsoncxx::builder::stream::finalize;
using bsoncxx::builder::stream::open_array;
using bsoncxx::builder::stream::open_document;
using namespace std;
using namespace crow;
using namespace mongocxx;

instance inst{};
const auto ur = uri{ "mongodb+srv://primitt:1016@primittdb.mvkeq.mongodb.net/" };
const auto dbconn = client{ ur };
const auto datadb = dbconn["LS"];
const auto coll = datadb["LS-SCORE"];

int main(){
    // query everything from ls-score
    SimpleApp app;
    CROW_ROUTE(app, "/")
    .websocket()
    .onopen([](websocket::connection& conn){
        cout << "connected to websocket" << endl;
    })
    .onmessage([](websocket::connection& conn, const string& data, bool is_binary){
        // get the string and split it 
        string command = data.substr(2);
        string id = data.substr(0, data.find("/"));
        if (command == "GETSCORE"){
            cout << "COMMAND: GETSCORE" << endl;
            // mongocxx query for the id
            auto cursor = coll.find(document{} << "id" << id << finalize);
            for (auto&& doc : cursor) {
                // send the score to the client
                conn.send_text(bsoncxx::to_json(doc));
            }
        }

    })
    .onclose([](websocket::connection& conn, const string& reason){
        cout << "closed connection" << reason << endl;
    });
    app.port(8080).multithreaded().run();
}
//FIXME: Segmentation fault after 5 clients connect, find a way to fix this

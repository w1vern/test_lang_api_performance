#include <drogon/drogon.h>
#include <drogon/HttpAppFramework.h>
#include <drogon/HttpController.h>
#include <drogon/HttpTypes.h>
#include <drogon/orm/DbClient.h>
#include <drogon/orm/DbTypes.h>
#include <iostream>
#include <string>

using namespace drogon;
using namespace drogon::orm;
using namespace std;

class DataModel {
public:
    string field1;
    int field2;
    
    DataModel(const string& f1, int f2) : field1(f1), field2(f2) {}
    
    Json::Value toJson() const {
        Json::Value json;
        json["field1"] = field1;
        json["field2"] = field2;
        return json;
    }
};

class ApiController : public drogon::HttpController<ApiController> {
private:
    DbClientPtr dbClient_;
    
public:
    ApiController(DbClientPtr dbClient) : dbClient_(dbClient) {}
    
    METHOD_LIST_BEGIN
        METHOD_ADD(ApiController::getData, "/api/test1", Get);
    METHOD_LIST_END
    
    void getData(const HttpRequestPtr& req,
                 std::function<void(const HttpResponsePtr&)>&& callback) {
        auto start = std::chrono::high_resolution_clock::now();
        
        // Asynchronous database query
        dbClient_->execSqlAsync(
            "SELECT field1, field2 FROM data WHERE field2 > 995",
            [callback, start](const Result& result) {
                Json::Value jsonArray;
                
                for (const auto& row : result) {
                    DataModel data(
                        row["field1"].as<string>(),
                        row["field2"].as<int>()
                    );
                    jsonArray.append(data.toJson());
                }
                
                auto resp = HttpResponse::newHttpJsonResponse(jsonArray);
                callback(resp);
                
                auto end = std::chrono::high_resolution_clock::now();
                auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
                LOG_DEBUG << "Request processed in " << duration.count() << "ms";
            },
            [callback](const DrogonDbException& e) {
                LOG_ERROR << "Database error: " << e.base().what();
                auto resp = HttpResponse::newHttpResponse();
                resp->setStatusCode(k500InternalServerError);
                resp->setBody("Database error");
                callback(resp);
            }
        );
    }
};

int main() {
    // Load environment variables from .env file
    auto& config = app().getCustomConfig();
    
    // Database configuration from environment
    string dbUser = getenv("DB_USER") ? getenv("DB_USER") : "";
    string dbPassword = getenv("DB_PASSWORD") ? getenv("DB_PASSWORD") : "";
    string dbHost = getenv("DB_IP") ? getenv("DB_IP") : "localhost";
    string dbPort = getenv("DB_PORT") ? getenv("DB_PORT") : "5432";
    string dbName = getenv("DB_NAME") ? getenv("DB_NAME") : "";
    
    // Construct connection string
    string connString = "host=" + dbHost +
                       " port=" + dbPort +
                       " dbname=" + dbName +
                       " user=" + dbUser +
                       " password=" + dbPassword;
    
    // Create asynchronous database client (PostgreSQL)
    auto dbClient = DbClient::newPgClient(connString, 10); // 10 connections in pool
    
    // Create controller with database dependency
    auto controller = std::make_shared<ApiController>(dbClient);
    
    // Configure app
    app().registerController(controller);
    app().addListener("0.0.0.0", 8001);
    app().setDocumentRoot("./");
    app().enableSession(0);
    
    // Set number of workers (threads)
    int workers = 4; // Can be configured
    app().setThreadNum(workers);
    
    LOG_INFO << "Server starting on http://0.0.0.0:8001";
    LOG_INFO << "Workers: " << workers;
    LOG_INFO << "API documentation available at /api/docs";
    
    app().run();
    
    return 0;
}
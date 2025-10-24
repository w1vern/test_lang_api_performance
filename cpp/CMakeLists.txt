cmake_minimum_required(VERSION 3.16)
project(MyFastApiApp)

set(CMAKE_CXX_STANDARD 17)

find_package(Drogon REQUIRED)
find_package(Jsoncpp REQUIRED)

add_executable(${PROJECT_NAME}
    main.cpp
)

target_link_libraries(${PROJECT_NAME} PRIVATE Drogon::Drogon Jsoncpp::Jsoncpp)
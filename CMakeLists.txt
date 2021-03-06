cmake_minimum_required(VERSION 3.14)

project(DebugStatus VERSION 0.1 LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

list(APPEND QML_DIRS
    "${CMAKE_CURRENT_SOURCE_DIR}/debug-helpers/"
    "${CMAKE_CURRENT_SOURCE_DIR}/debug-helpers/test-controls"
    "${CMAKE_CURRENT_SOURCE_DIR}/debug-helpers/status-desktop/"
    "${CMAKE_CURRENT_SOURCE_DIR}/status-desktop/ui/imports"
    "${CMAKE_CURRENT_SOURCE_DIR}/status-desktop/ui/app"
    "${CMAKE_CURRENT_SOURCE_DIR}/status-desktop/ui/StatusQ/src/"
)
set(QML_IMPORT_PATH "${QML_DIRS}" CACHE STRING "Qt Creator extra qml import paths")
set(QML2_IMPORT_PATH "${QML_DIRS}" CACHE STRING "Qt Creator extra qml import paths")

find_package(QT NAMES Qt6 Qt5 COMPONENTS Core Quick REQUIRED)
find_package(Qt${QT_VERSION_MAJOR} COMPONENTS Core Quick REQUIRED)

set(PROJECT_SOURCES
    debug-helpers/main.cpp

    debug-helpers/main.qml

    CMakeLists.txt
)

if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(${PROJECT_NAME}
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
    )
# Define target properties for Android with Qt 6 as:
#    set_property(TARGET ${PROJECT_NAME} APPEND PROPERTY QT_ANDROID_PACKAGE_SOURCE_DIR
#                 ${CMAKE_CURRENT_SOURCE_DIR}/android)
# For more information, see https://doc.qt.io/qt-6/qt-add-executable.html#target-creation
else()
    if(ANDROID)
        add_library(${PROJECT_NAME} SHARED
            ${PROJECT_SOURCES}
        )
# Define properties for Android with Qt 5 after find_package() calls as:
#    set(ANDROID_PACKAGE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android")
    else()
        add_executable(${PROJECT_NAME}
          ${PROJECT_SOURCES}
        )
    endif()
endif()

file(GLOB_RECURSE QML_FILES CONFIGURE_DEPENDS ${PROJECT_SOURCE_DIR}/status-desktop/ui/*.qml)
set_property(TARGET ${PROJECT_NAME} APPEND PROPERTY SOURCES ${QML_FILES})

target_compile_definitions(${PROJECT_NAME}
  PRIVATE $<$<OR:$<CONFIG:Debug>,$<CONFIG:RelWithDebInfo>>:QT_QML_DEBUG>)
target_link_libraries(${PROJECT_NAME}
  PRIVATE Qt${QT_VERSION_MAJOR}::Core Qt${QT_VERSION_MAJOR}::Quick)

set_target_properties(${PROJECT_NAME} PROPERTIES
    MACOSX_BUNDLE_GUI_IDENTIFIER localtest.dev
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

# The CMAKE_SYSTEM_PROCESSOR is overwritten with arm on M1 here: build/CMakeFiles/3.21.1/CMakeSystem.cmake; it should be x86_64
message("CMAKE_SYSTEM_PROCESSOR: " ${CMAKE_SYSTEM_PROCESSOR} "; CMAKE_OSX_ARCHITECTURES: " ${CMAKE_OSX_ARCHITECTURES})

if(QT_VERSION_MAJOR EQUAL 6)
    qt_import_qml_plugins(${PROJECT_NAME})
    qt_finalize_executable(${PROJECT_NAME})
endif()

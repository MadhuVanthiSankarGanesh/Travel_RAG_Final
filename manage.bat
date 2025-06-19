@echo off
setlocal

IF "%1"=="build" (
    docker-compose build
    GOTO :EOF
)

IF "%1"=="start" (
    docker-compose up -d
    GOTO :EOF
)

IF "%1"=="stop" (
    docker-compose down
    GOTO :EOF
)

IF "%1"=="logs" (
    docker-compose logs -f
    GOTO :EOF
)

IF "%1"=="crawl" (
    docker-compose run --rm crawler
    GOTO :EOF
)

IF "%1"=="restart" (
    docker-compose restart
    GOTO :EOF
)

IF "%1"=="clean" (
    docker-compose down -v
    rmdir /s /q qdrant_data
    GOTO :EOF
)

echo Usage: %0 {build^|start^|stop^|logs^|crawl^|restart^|clean}
echo.
echo Commands:
echo   build   - Build all Docker images
echo   start   - Start all services
echo   stop    - Stop all services
echo   logs    - View logs from all services
echo   crawl   - Run the Wikipedia crawler
echo   restart - Restart all services
echo   clean   - Remove all data and volumes 
#!/bin/bash

case "$1" in
    "build")
        docker-compose build
        ;;
    "start")
        docker-compose up -d
        ;;
    "stop")
        docker-compose down
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "crawl")
        docker-compose run --rm crawler
        ;;
    "restart")
        docker-compose restart
        ;;
    "clean")
        docker-compose down -v
        rm -rf qdrant_data/*
        ;;
    *)
        echo "Usage: $0 {build|start|stop|logs|crawl|restart|clean}"
        exit 1
        ;;
esac 
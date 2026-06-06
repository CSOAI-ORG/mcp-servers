#!/bin/bash
# MEOK AI Labs - Setup Script
# Run this to set up the development environment

set -e

echo "=============================================="
echo "MEOK AI Labs - Development Setup"
echo "=============================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prereqs() {
    log_info "Checking prerequisites..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed."
        exit 1
    fi
    if ! command -v docker &> /dev/null; then
        log_warn "Docker not found. Some features may not work."
    fi
    log_info "Prerequisites OK"
}

setup_env() {
    log_info "Setting up environment..."
    if [ ! -f .env ]; then
        cp .env.example .env 2>/dev/null || true
        log_info "Created .env from .env.example"
        log_warn "Please edit .env and add your API keys!"
    fi
}

install_python() {
    log_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r api/requirements.txt
    pip install -r workers/requirements.txt
    pip install -r tests/requirements.txt
    log_info "Python dependencies installed"
}

install_node() {
    if [ -f package.json ]; then
        log_info "Installing Node dependencies..."
        npm install
    fi
}

setup_docker() {
    if command -v docker &> /dev/null; then
        log_info "Building Docker images..."
        docker-compose -f docker-compose.infra.yml build || true
    fi
}

main() {
    check_prereqs
    setup_env
    install_python
    install_node
    setup_docker
    echo ""
    echo "=============================================="
    echo "Setup Complete!"
    echo "=============================================="
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env and add your API keys"
    echo "  2. docker-compose -f docker-compose.infra.yml up -d"
    echo "  3. cd api && uvicorn server:app --reload"
    echo "  4. Or: make dev"
    echo ""
}

main "$@"

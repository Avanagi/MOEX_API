# ============================================================================
# run.ps1 — Управление Docker-контейнерами MOEX_API (PowerShell)
# ============================================================================
# Запуск: .\run.ps1 build | up | down | logs | restart | rebuild | status
# ============================================================================


$RED    = [ConsoleColor]::Red
$GREEN  = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::DarkYellow
$BLUE   = [ConsoleColor]::Blue
$CYAN   = [ConsoleColor]::Cyan


$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$COMPOSE_FILE = Join-Path $SCRIPT_DIR "docker-compose.yml"
$ENV_FILE = Join-Path $SCRIPT_DIR "backend\.env"
$ENV_EXAMPLE = Join-Path $SCRIPT_DIR "backend\.env.example"


function Write-Info  { Write-Host $args -ForegroundColor $GREEN  }
function Write-Warn  { Write-Host $args -ForegroundColor $YELLOW }
function Write-Error { Write-Host $args -ForegroundColor $RED   }
function Write-Title { Write-Host $args -ForegroundColor $CYAN  }

function Check-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "[ERROR] docker not found. Please install Docker Desktop."
        exit 1
    }
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Docker is not running. Please start Docker Desktop."
        exit 1
    }
    Write-Info "[OK] Docker is ready"
}

function Check-ComposeFile {
    if (-not (Test-Path $COMPOSE_FILE)) {
        Write-Error "[ERROR] docker-compose.yml not found in $SCRIPT_DIR"
        exit 1
    }
}

function Check-Env {
    if (-not (Test-Path $ENV_FILE)) {
        if (Test-Path $ENV_EXAMPLE) {
            Copy-Item $ENV_EXAMPLE $ENV_FILE
            Write-Info "[OK] .env file created from .env.example"
        } else {
            Write-Warn "[WARN] .env file not found, continuing anyway..."
        }
    }
}

function Show-Help {
    Write-Title ""
    Write-Title "============================================================================"
    Write-Title "       MOEX_API - Docker Container Management"
    Write-Title "============================================================================"
    Write-Title ""
    Write-Info  "  build              Build all Docker images"
    Write-Info  "  up                 Start all services"
    Write-Info  "  down               Stop and remove containers"
    Write-Info  "  logs               Show all service logs (follow)"
    Write-Info  "  logs-collector     Show collector logs only (follow)"
    Write-Info  "  restart            Restart all services"
    Write-Info  "  restart-collector  Restart collector only"
    Write-Info  "  rebuild            Full rebuild without cache"
    Write-Info  "  status             Show container status"
    Write-Info  "  ps                 Same as status"
    Write-Info  "  help               Show this help"
    Write-Title ""
    Write-Info " Examples:"
    Write-Info "  .\run.ps1 build    # Build images"
    Write-Info "  .\run.ps1 up       # Start everything"
    Write-Info "  .\run.ps1 logs-collector  # Show collector logs"
    Write-Title ""
}

function Cmd-Build { 
    Check-Docker
    Check-ComposeFile
    Check-Env
    Write-Info "[BUILD] Building Docker images..."
    docker-compose -f $COMPOSE_FILE build
    if ($LASTEXITCODE -eq 0) {
        Write-Info "[OK] Build completed"
    } else {
        Write-Error "[ERROR] Build failed"
        exit 1
    }
}

function Cmd-Up { 
    Check-Docker
    Check-ComposeFile
    Check-Env
    Write-Info "[START] Starting all services..."
    docker-compose -f $COMPOSE_FILE up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Info "[OK] All services started"
        Write-Info ""
        Cmd-Status
    } else {
        Write-Error "[ERROR] Failed to start services"
        exit 1
    }
}

function Cmd-Down { 
    Check-Docker
    Write-Warn "[STOP] Stopping all services..."
    docker-compose -f $COMPOSE_FILE down
    Write-Info "[OK] Containers stopped and removed"
}

function Cmd-Logs { 
    Check-Docker
    Write-Info "[LOGS] Showing all service logs (Ctrl+C to exit)..."
    docker-compose -f $COMPOSE_FILE logs -f
}

function Cmd-LogsCollector { 
    Check-Docker
    Write-Info "[LOGS] Showing collector logs (Ctrl+C to exit)..."
    docker-compose -f $COMPOSE_FILE logs -f collector
}

function Cmd-Restart { 
    Check-Docker
    Write-Warn "[RESTART] Restarting all services..."
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE up -d
    Write-Info "[OK] Services restarted"
    Cmd-Status
}

function Cmd-RestartCollector { 
    Check-Docker
    Write-Warn "[RESTART] Restarting collector..."
    docker-compose -f $COMPOSE_FILE restart collector
    Write-Info "[OK] Collector restarted"
    Write-Info "[LOGS] Showing logs..."
    docker-compose -f $COMPOSE_FILE logs -f collector
}

function Cmd-Rebuild { 
    Check-Docker
    Check-ComposeFile
    Check-Env
    Write-Warn "[REBUILD] Full rebuild without cache..."
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Info "[OK] Build completed"
        Write-Info "[START] Starting services..."
        docker-compose -f $COMPOSE_FILE up -d
        Write-Info "[OK] Done!"
        Cmd-Status
    } else {
        Write-Error "[ERROR] Build failed"
        exit 1
    }
}

function Cmd-Status { 
    Check-Docker
    Write-Info "[STATUS] Container status:"
    docker-compose -f $COMPOSE_FILE ps
}


if ($args.Count -eq 0) {
    Show-Help
    exit 0
}

$cmd = $args[0].ToLower()

switch ($cmd) {
    "build"       { Cmd-Build }
    "up"          { Cmd-Up }
    "down"        { Cmd-Down }
    "logs"        { Cmd-Logs }
    "logs-collector" { Cmd-LogsCollector }
    "restart"     { Cmd-Restart }
    "restart-collector" { Cmd-RestartCollector }
    "rebuild"     { Cmd-Rebuild }
    "status"      { Cmd-Status }
    "ps"          { Cmd-Status }
    "help"        { Show-Help }
    "--help"      { Show-Help }
    "-h"          { Show-Help }
    default {
        Write-Error "[ERROR] Unknown command: $cmd"
        Write-Host ""
        Show-Help
        exit 1
    }
}
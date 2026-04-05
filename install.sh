#!/bin/bash
set -e

echo "🚀 Installing ragy..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
major_version=$(echo "$python_version" | cut -d. -f1)
minor_version=$(echo "$python_version" | cut -d. -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 12 ]); then
    echo "❌ Python 3.12+ required. Found: $python_version"
    echo "   Please upgrade Python and try again."
    exit 1
fi

echo "✓ Python $python_version detected"
echo ""

if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✓ uv installed"
    echo ""
fi

echo "📥 Cloning ragy repository..."
if [ -d "ragy" ]; then
    echo "⚠️  ragy directory already exists. Skipping clone."
    cd ragy
else
    git clone https://github.com/Arseni1919/ragy.git
    cd ragy
fi
echo ""

echo "📦 Installing dependencies..."
uv sync
echo "✓ Dependencies installed"
echo ""

echo "⚙️  Creating .env configuration file..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping creation."
else
    echo ""
    echo "📝 RAGY requires a Tavily API key for web search functionality."
    echo "   You can get a free API key at: https://tavily.com/"
    echo ""
    read -p "Enter your Tavily API key (or press Enter to skip): " tavily_key < /dev/tty

    cat > .env << EOF
# Required API Key
TAVILY_API_KEY="${tavily_key}"

# Embedding Configuration
HF_EMB_MODEL="all-MiniLM-L6-v2"

# Database & Performance
DB_PATH="./ragy_db"
RAGY_MAX_CONCURRENT=10

# API Server
API_HOST="0.0.0.0"
API_PORT=8000

# Background Jobs
SCHEDULER_ENABLED=true
SCHEDULER_HOUR=2
SCHEDULER_TIMEZONE="UTC"
JOBS_DB_PATH="./ragy_jobs.db"
EOF
    echo "✓ .env file created"
fi
echo ""

echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if API key was provided
if [ -f ".env" ]; then
    if grep -q 'TAVILY_API_KEY=""' .env; then
        echo "⚠️  IMPORTANT: Tavily API Key Required"
        echo ""
        echo "  To use RAGY, you need a Tavily API key:"
        echo ""
        echo "  1. Get your FREE API key at: https://tavily.com/"
        echo "  2. Edit .env file and add your key:"
        echo "     nano .env"
        echo "     (Replace empty TAVILY_API_KEY with your actual key)"
        echo ""
    else
        echo "✓ Tavily API key configured"
        echo ""
    fi
fi

echo "📝 Next steps:"
echo ""
echo "  1. Start the API server:"
echo "     uv run uvicorn ragy_api.main:app --reload"
echo ""
echo "  2. In another terminal, start the CLI:"
echo "     cd ragy"
echo "     uv run ragy"
echo ""
echo "  3. Access API documentation:"
echo "     http://localhost:8000/docs"
echo ""
echo "💡 First Run Tip:"
echo "   With fast internet, start the CLI right away!"
echo "   Embedding models (~80MB) download in background."
echo "   First query may take 10-30 seconds while models load."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation: https://github.com/Arseni1919/ragy"
echo "🔑 Get API key: https://tavily.com/"
echo ""

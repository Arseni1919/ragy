#!/bin/bash
set -e

echo "🚀 Installing RagyApp..."
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

echo "📥 Cloning RagyApp repository..."
if [ -d "RagyApp" ]; then
    echo "⚠️  RagyApp directory already exists. Skipping clone."
    cd RagyApp
else
    git clone https://github.com/YOUR_USERNAME/RagyApp.git
    cd RagyApp
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
    cat > .env << 'EOF'
# Required API Keys
TAVILY_API_KEY="your-tavily-api-key-here"
GEMINI_API_KEY="your-gemini-api-key-here"

# Optional Configuration (defaults shown)
HF_EMB_MODEL="all-MiniLM-L6-v2"
DB_PATH="./ragy_db"
RAGY_MAX_CONCURRENT=10
API_HOST="0.0.0.0"
API_PORT=8000
SCHEDULER_ENABLED=true
SCHEDULER_HOUR=2
SCHEDULER_TIMEZONE="UTC"
EOF
    echo "✓ .env file created"
fi
echo ""

echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo ""
echo "  1. Edit .env file with your API keys:"
echo "     nano .env"
echo ""
echo "  2. Start the API server:"
echo "     uv run uvicorn ragy_api.main:app --reload"
echo ""
echo "  3. In another terminal, start the CLI:"
echo "     cd RagyApp"
echo "     uv run ragy"
echo ""
echo "  4. Access API documentation:"
echo "     http://localhost:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation: https://github.com/YOUR_USERNAME/RagyApp"
echo "🐛 Issues: https://github.com/YOUR_USERNAME/RagyApp/issues"
echo ""

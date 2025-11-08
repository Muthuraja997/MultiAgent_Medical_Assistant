#!/bin/bash
# ============================================================================
# Multi-Agent Medical Assistant - Quick Setup Script
# ============================================================================
# 
# This script automates the setup process for the medical assistant.
# Supports: Cloud (Azure), Open-Source (Ollama), or Hybrid setups.
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Python version
check_python() {
    print_header "Checking Python Installation"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "Please install Python 3.11 or higher"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Found Python $PYTHON_VERSION"
    
    # Check if version is >= 3.11
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
        print_warning "Python 3.11+ is recommended, but older version found"
    fi
    
    print_success "Python check passed"
}

# Create virtual environment
setup_venv() {
    print_header "Setting Up Python Virtual Environment"
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            print_info "Using existing virtual environment"
            return
        fi
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created"
    
    # Activate it
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    print_success "Virtual environment activated"
}

# Install dependencies
install_deps() {
    print_header "Installing Dependencies"
    
    # Activate venv first
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    
    print_info "Installing requirements.txt..."
    pip install -r requirements.txt
    
    print_success "Dependencies installed"
}

# Setup choice
choose_setup() {
    print_header "Choose Your Setup Type"
    
    echo ""
    echo "1) Cloud Setup (Azure OpenAI + Qdrant Cloud)"
    echo "   - Best for: Production, team projects"
    echo "   - Cost: \$\$\$ (per API call)"
    echo "   - Speed: Fast (depends on API latency)"
    echo ""
    echo "2) Open-Source Setup (Ollama + Local Qdrant)"
    echo "   - Best for: Local development, testing"
    echo "   - Cost: \$ (local compute only)"
    echo "   - Speed: Slower initially, but free"
    echo ""
    echo "3) Hybrid Setup (Azure OpenAI + Local Qdrant)"
    echo "   - Best for: Balance of cost and convenience"
    echo "   - Cost: \$\$ (balanced)"
    echo "   - Speed: Very fast"
    echo ""
    
    read -p "Select setup (1-3): " SETUP_CHOICE
    
    case $SETUP_CHOICE in
        1)
            SETUP_TYPE="cloud"
            print_success "Selected: Cloud Setup (Azure OpenAI)"
            ;;
        2)
            SETUP_TYPE="opensource"
            print_success "Selected: Open-Source Setup (Ollama)"
            ;;
        3)
            SETUP_TYPE="hybrid"
            print_success "Selected: Hybrid Setup"
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Setup Cloud configuration
setup_cloud() {
    print_header "Cloud Setup Configuration"
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    print_info "You'll need the following from Azure:"
    echo "  - deployment_name (e.g., gpt-4o-deployment)"
    echo "  - model_name (e.g., gpt-4o)"
    echo "  - azure_endpoint (e.g., https://your-resource.openai.azure.com/)"
    echo "  - openai_api_key"
    echo "  - openai_api_version (e.g., 2024-05-01)"
    echo ""
    
    read -p "Enter deployment_name: " DEPLOYMENT_NAME
    read -p "Enter model_name: " MODEL_NAME
    read -p "Enter azure_endpoint: " AZURE_ENDPOINT
    read -sp "Enter openai_api_key: " OPENAI_API_KEY
    echo
    read -p "Enter openai_api_version (default: 2024-05-01): " OPENAI_API_VERSION
    OPENAI_API_VERSION=${OPENAI_API_VERSION:-2024-05-01}
    
    # Create .env file
    cat > .env << EOF
# Cloud Setup - Azure OpenAI
deployment_name=$DEPLOYMENT_NAME
model_name=$MODEL_NAME
azure_endpoint=$AZURE_ENDPOINT
openai_api_key=$OPENAI_API_KEY
openai_api_version=$OPENAI_API_VERSION

# Embeddings (can be same or different endpoint)
embedding_deployment_name=$DEPLOYMENT_NAME
embedding_model_name=$MODEL_NAME
embedding_azure_endpoint=$AZURE_ENDPOINT
embedding_openai_api_key=$OPENAI_API_KEY
embedding_openai_api_version=$OPENAI_API_VERSION

# Optional: Web Search
# TAVILY_API_KEY=your-tavily-api-key

# Optional: Speech
# ELEVEN_LABS_API_KEY=your-elevenlabs-api-key

# Optional: Qdrant Cloud
# QDRANT_URL=your-qdrant-url
# QDRANT_API_KEY=your-qdrant-api-key
EOF
    
    print_success ".env file created with Cloud configuration"
}

# Setup Open-Source configuration
setup_opensource() {
    print_header "Open-Source Setup Configuration"
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        print_warning "Ollama is not installed"
        echo ""
        echo "Installation instructions:"
        echo "  macOS/Linux: https://ollama.ai/download"
        echo "  Windows: https://ollama.ai/download/windows"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Ollama is installed"
    fi
    
    # Create minimal .env
    cat > .env << EOF
# Open-Source Setup (Ollama)
# 
# Make sure Ollama is running:
#   ollama serve
#
# Then modify config.py to use OllamaLLM instead of AzureChatOpenAI
# See SETUP_GUIDE.md for detailed instructions

# No API keys needed for local setup!
EOF
    
    print_success ".env file created (minimal config for local setup)"
    
    print_info "Next steps:"
    echo "  1. Install Ollama from https://ollama.ai"
    echo "  2. Run: ollama serve (in a separate terminal)"
    echo "  3. Pull a model: ollama pull mistral"
    echo "  4. Follow instructions in SETUP_GUIDE.md to modify config.py"
}

# Setup Hybrid configuration
setup_hybrid() {
    print_header "Hybrid Setup Configuration"
    
    print_info "You'll need Azure OpenAI keys for LLM and embeddings"
    echo "  Qdrant will run locally at ./data/qdrant_db/"
    echo ""
    
    read -p "Enter deployment_name: " DEPLOYMENT_NAME
    read -p "Enter model_name: " MODEL_NAME
    read -p "Enter azure_endpoint: " AZURE_ENDPOINT
    read -sp "Enter openai_api_key: " OPENAI_API_KEY
    echo
    read -p "Enter openai_api_version (default: 2024-05-01): " OPENAI_API_VERSION
    OPENAI_API_VERSION=${OPENAI_API_VERSION:-2024-05-01}
    
    # Create .env file
    cat > .env << EOF
# Hybrid Setup - Azure OpenAI LLM + Local Qdrant
deployment_name=$DEPLOYMENT_NAME
model_name=$MODEL_NAME
azure_endpoint=$AZURE_ENDPOINT
openai_api_key=$OPENAI_API_KEY
openai_api_version=$OPENAI_API_VERSION

# Embeddings
embedding_deployment_name=$DEPLOYMENT_NAME
embedding_model_name=$MODEL_NAME
embedding_azure_endpoint=$AZURE_ENDPOINT
embedding_openai_api_key=$OPENAI_API_KEY
embedding_openai_api_version=$OPENAI_API_VERSION

# Local Qdrant (no keys needed)
# Uses ./data/qdrant_db/

# Optional: Web Search and Speech APIs
# TAVILY_API_KEY=your-tavily-api-key
# ELEVEN_LABS_API_KEY=your-elevenlabs-api-key
EOF
    
    print_success ".env file created with Hybrid configuration"
}

# Create necessary directories
create_dirs() {
    print_header "Creating Necessary Directories"
    
    mkdir -p data/raw
    mkdir -p data/parsed_docs
    mkdir -p uploads/backend
    mkdir -p uploads/frontend
    mkdir -p uploads/skin_lesion_output
    mkdir -p uploads/speech
    
    print_success "Directories created"
}

# Test LLM connection
test_setup() {
    print_header "Testing Your Setup"
    
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    print_info "Testing LLM connection..."
    
    # Create a test script
    cat > test_setup.py << 'EOF'
import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("Testing Multi-Agent Medical Assistant Setup")
print("="*60 + "\n")

# Test 1: Check environment variables
print("1. Checking environment variables...")
required_vars = [
    'deployment_name', 'model_name', 'azure_endpoint', 
    'openai_api_key', 'openai_api_version',
    'embedding_deployment_name', 'embedding_model_name'
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"   ⚠️  Missing variables: {', '.join(missing_vars)}")
    print("   This is OK for open-source setup (Ollama)")
else:
    print("   ✅ All environment variables found")

# Test 2: Try to import config
print("\n2. Testing config import...")
try:
    from config import Config
    config = Config()
    print("   ✅ Config loaded successfully")
except Exception as e:
    print(f"   ❌ Config error: {e}")
    sys.exit(1)

# Test 3: Test LLM (if available)
print("\n3. Testing LLM...")
try:
    response = config.agent_decision.llm.invoke("Say 'Hello'")
    print(f"   ✅ LLM working! Response: {str(response)[:50]}...")
except Exception as e:
    print(f"   ❌ LLM error: {e}")
    print("   Make sure Azure OpenAI keys are correct or Ollama is running")

# Test 4: Test vector store
print("\n4. Testing vector database...")
try:
    from agents.rag_agent import MedicalRAG
    rag = MedicalRAG(config)
    print("   ✅ Vector database initialized")
except Exception as e:
    print(f"   ⚠️  Vector database error: {e}")
    print("   This is OK, run document ingestion when ready")

print("\n" + "="*60)
print("Setup test complete!")
print("="*60 + "\n")
EOF
    
    python test_setup.py
    rm test_setup.py
}

# Show next steps
show_next_steps() {
    print_header "Setup Complete! Next Steps"
    
    echo ""
    echo "1. Verify your .env file:"
    echo "   cat .env"
    echo ""
    
    if [ "$SETUP_TYPE" == "opensource" ]; then
        echo "2. Start Ollama in a separate terminal:"
        echo "   ollama serve"
        echo ""
        echo "3. Pull a model:"
        echo "   ollama pull mistral"
        echo ""
        echo "4. Modify config.py to use Ollama (see SETUP_GUIDE.md)"
        echo ""
    fi
    
    echo "5. Ingest medical documents:"
    echo "   python ingest_rag_data.py --input data/raw/"
    echo ""
    echo "6. Start the server:"
    echo "   python app.py"
    echo ""
    echo "7. Open in browser:"
    echo "   http://localhost:8000"
    echo ""
    
    print_info "Full documentation: see SETUP_GUIDE.md"
}

# Main execution
main() {
    echo ""
    print_header "Multi-Agent Medical Assistant - Setup"
    
    check_python
    setup_venv
    install_deps
    create_dirs
    choose_setup
    
    case $SETUP_TYPE in
        cloud)
            setup_cloud
            ;;
        opensource)
            setup_opensource
            ;;
        hybrid)
            setup_hybrid
            ;;
    esac
    
    test_setup
    show_next_steps
    
    print_success "Setup script completed successfully!"
}

main

#!/bin/bash
# Resource checker for test environment

echo "=== System Resource Check ==="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

# Check available memory
MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEMORY_GB=$((MEMORY_KB / 1024 / 1024))
echo "📊 Total Memory: ${MEMORY_GB}GB"

# Check free memory
FREE_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
FREE_GB=$((FREE_KB / 1024 / 1024))
echo "🆓 Available Memory: ${FREE_GB}GB"

# Check CPU
CPU_CORES=$(nproc)
echo "🖥️  CPU Cores: ${CPU_CORES}"

# Make recommendation
echo ""
echo "=== Testing Recommendation ==="

if [ $FREE_GB -lt 2 ]; then
    echo "⚠️  CRITICAL: Less than 2GB available"
    echo "   → Skip testing or use CI/CD"
    exit 1
elif [ $FREE_GB -lt 4 ]; then
    echo "⚠️  LOW: 2-4GB available"
    echo "   → Use Bronze Level (static validation only)"
    echo "   → Command: python3 config-validator.py"
elif [ $FREE_GB -lt 8 ]; then
    echo "✅ OK: 4-8GB available"
    echo "   → Use Silver Level (minimal ES test)"
    echo "   → Command: ./test-elasticsearch-minimal.sh"
else
    echo "✅ EXCELLENT: 8GB+ available"
    echo "   → Can run Gold Level (full test)"
    echo "   → Command: ./tests/setup_test_env.sh"
fi

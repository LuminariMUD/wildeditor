#!/bin/bash

# Test script to debug the directory issue
echo "Testing directory paths..."

# Test 1: Direct path
echo "Test 1: cd /opt/wildeditor-mcp"
cd /opt/wildeditor-mcp 2>/dev/null && echo "✅ Direct path works" || echo "❌ Direct path failed"

# Test 2: Using variable
APP_DIR="/opt/wildeditor-mcp"
echo "Test 2: APP_DIR variable = '$APP_DIR'"
cd $APP_DIR 2>/dev/null && echo "✅ Variable path works" || echo "❌ Variable path failed"

# Test 3: Show what the variable actually contains
echo "Test 3: Variable content analysis"
echo "APP_DIR length: ${#APP_DIR}"
echo "APP_DIR hex dump:"
echo -n "$APP_DIR" | hexdump -C

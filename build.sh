#!/bin/bash
# Build script for Vercel deployment

echo "Building React frontend..."

# Navigate to the static directory
cd app/static

# Install dependencies
echo "Installing Node dependencies..."
npm install

# Build the React app
echo "Building React app..."
npm run build

# Verify build output
if [ -d "build" ]; then
    echo "React build completed successfully!"
    echo "Build output:"
    ls -la build/
else
    echo "Build failed - build directory not found"
    exit 1
fi

echo "Build process complete!"

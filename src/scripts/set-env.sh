#!/bin/bash
# set-env.sh - Set JAVA_HOME, PATH, and Go environment variables
# Source this script: source ./set-env.sh

# Find Java installation
find_java_home() {
    local java_paths=(
        "/usr/lib/jvm/java-17-openjdk*"
        "/usr/lib/jvm/java-11-openjdk*"
        "/usr/lib/jvm/java-*-openjdk*"
        "/usr/lib/jvm/default-java"
        "/opt/jdk*"
        "/opt/java*"
        "$HOME/.local/java*"
        "$HOME/.jdks/*"
    )
    
    for pattern in "${java_paths[@]}"; do
        if ls $pattern 1> /dev/null 2>&1; then
            local jdk_dir=$(ls -d $pattern 2>/dev/null | head -1)
            if [ -d "$jdk_dir" ]; then
                # If it's a symlink, resolve it
                if [ -L "$jdk_dir" ]; then
                    jdk_dir=$(readlink -f "$jdk_dir")
                fi
                echo "$jdk_dir"
                return 0
            fi
        fi
    done
    return 1
}

# Find Go installation
find_go_home() {
    local go_paths=(
        "/usr/local/go"
        "/opt/go"
        "$HOME/go"
        "$HOME/.go"
        "$HOME/.local/go"
    )
    
    for path in "${go_paths[@]}"; do
        if [ -d "$path" ] && [ -x "$path/bin/go" ]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

# Set Java environment
set_java_env() {
    local java_home=$(find_java_home)
    if [ -n "$java_home" ]; then
        export JAVA_HOME="$java_home"
        export PATH="$JAVA_HOME/bin:$PATH"
        echo "JAVA_HOME set to: $JAVA_HOME"
        if [ -x "$JAVA_HOME/bin/java" ]; then
            java -version 2>&1 | head -1
        fi
    else
        echo "Warning: Could not find Java installation"
    fi
}

# Set Go environment
set_go_env() {
    local go_home=$(find_go_home)
    if [ -n "$go_home" ]; then
        export GOROOT="$go_home"
        export GOPATH="$HOME/go"
        export PATH="$GOROOT/bin:$GOPATH/bin:$PATH"
        echo "GOROOT set to: $GOROOT"
        echo "GOPATH set to: $GOPATH"
        if [ -x "$GOROOT/bin/go" ]; then
            go version
        fi
    else
        echo "Warning: Could not find Go installation"
    fi
}

# Main
echo "Setting up Java and Go environment..."
echo "======================================"
set_java_env
echo "--------------------------------------"
set_go_env
echo "======================================"
echo "Environment setup complete!"
echo ""
echo "Current settings:"
echo "  JAVA_HOME: $JAVA_HOME"
echo "  GOROOT: $GOROOT"
echo "  GOPATH: $GOPATH"
echo "  PATH includes:"
echo "    - \$JAVA_HOME/bin"
echo "    - \$GOROOT/bin"
echo "    - \$GOPATH/bin"

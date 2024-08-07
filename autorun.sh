# Check if Python is installed and version is 3.11 or higher
if command -v python3 &>/dev/null; then
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    if (( $(echo "$python_version >= 3.11" | bc -l) )); then
        echo "Python 3.11 or higher is already installed."
        pip3 install -r requirements.txt
        echo "installing requirements"
        export FLASK_APP=app.py
        echo "exporting FLASK_APP environment variable"
        export FLASK_ENV=development
        echo "exporting FLASK_ENV environment variable"

        flask db init
        echo "initializing database"
        flask db migrate -m "Add organisation_email to Organisation"
        echo "migrating database"
        flask db upgrade
        echo "upgrading database"

        echo "Running the application..."
        flask run
    else
        echo "Python version is below 3.11. Installing Python..."
        if [[ $(uname) == "Darwin" ]]; then
            # Install Python on macOS
            brew install python@3.11
        elif [[ $(uname) == "Linux" ]]; then
            # Install Python on Linux
            sudo apt-get update
            sudo apt-get install python3.11
        else
            echo "Unsupported operating system. Exiting..."
            exit 1
        fi

        # Verify if Python is installed again
        if command -v python3 &>/dev/null; then
            python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
            if (( $(echo "$python_version >= 3.11" | bc -l) )); then
                echo "Python 3.11 or higher is installed."
                pip3 install -r requirements.txt
            else
                echo "Python installation failed. Exiting..."
                exit 1
            fi
        else
            echo "Python installation failed. Exiting..."
            exit 1
        fi
    fi
else
    echo "Python is not installed. Exiting..."
    exit 1
fi

# Check if the operating system is Windows
if [[ $(uname) == "MINGW"* ]]; then
    echo "Running autorun.bat..."
    autorun.bat
fi

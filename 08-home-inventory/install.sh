# Stop script if a command fails
set -e

# Create python virtual environment and activate it.
python3 -m venv ./venv || echo "failed to make venv"
source ./venv/bin/activate
echo "  *********************"
echo "  Python virtual env created"
echo "  *********************"

# Install python dependencies.
pip install -r reqs.txt || echo "failed to pip install py reqs"
echo "  *********************"
echo "  Python dependencies installed"
echo "  *********************"

# Install javascript dependencies.
cd ./app/static/
npm install || echo "failed to npm install"
cd -
echo "  *********************"
echo "  JS dependencies installed"
echo "  *********************"

echo ""
echo "  *********************"
echo "  *********************"
echo "  Install complete!"
echo "  *********************"
echo "  *********************"
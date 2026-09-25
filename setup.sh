#!/bin/bash
# ====================================================
# Restaurant Portal - Setup Script
# ====================================================

set -e

echo "🍽️  Setting up Restaurant Portal..."

# 1. Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 4. Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# 5. Create .env file from example if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your database credentials"
fi

# 6. Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs media static/css static/js staticfiles

# 7. Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# 8. Create superuser
echo "👤 Creating superuser..."
python manage.py createsuperuser || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Visit http://localhost:8000/admin/ to access the admin panel."
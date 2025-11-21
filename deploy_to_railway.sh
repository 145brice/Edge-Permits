#!/bin/bash
echo "🚀 Edge Permits Railway Deployment Script"
echo "=========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
fi

# Login to Railway (user will need to authenticate)
echo "Please login to Railway (browser will open):"
railway login

# Create new project
echo "Creating Railway project..."
railway init edge-permits-saas

# Link to GitHub
echo "Linking to GitHub repository..."
railway link --project edge-permits-saas

# Set environment variables
echo "Setting environment variables..."
railway variables set SECRET_KEY="your_secret_key_here"
railway variables set STRIPE_SECRET_KEY="sk_live_your_stripe_secret_key"
railway variables set STRIPE_PUBLISHABLE_KEY="pk_live_your_stripe_publishable_key"
railway variables set STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
railway variables set STRIPE_PRICE_ID="price_your_price_id"
railway variables set FIREBASE_CREDENTIALS_PATH="/app/firebase-credentials.json"
railway variables set FIREBASE_DATABASE_URL="https://your-project.firebaseio.com/"
railway variables set SENDGRID_API_KEY="SG.your_sendgrid_api_key"
railway variables set FROM_EMAIL="noreply@edgepermits.com"
railway variables set FLASK_ENV="production"
railway variables set DATABASE_PATH="contractor_leads.db"

# Deploy
echo "Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "Your app will be available at the URL shown in Railway dashboard"
echo ""
echo "Next steps:"
echo "1. Go to Railway dashboard"
echo "2. Upload firebase-credentials.json to the /app directory"
echo "3. Update environment variables with real values"
echo "4. Test your live app!"

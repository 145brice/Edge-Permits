# Stripe Payment Links Metadata Configuration

## ⚠️ IMPORTANT: Required for Webhooks to Work

Your Stripe payment links **must include metadata** for the webhook to automatically create subscriptions.

## How to Add Metadata to Stripe Payment Links

### 1. Go to Stripe Dashboard
1. Login to [dashboard.stripe.com](https://dashboard.stripe.com)
2. Navigate to **Payment Links** (or **Products** → **Payment Links**)

### 2. Edit Each Payment Link

For each of your 4 payment links, add this metadata:

#### Nashville Payment Link
**URL**: https://buy.stripe.com/4gM14pc1G7ij5XYfXx63K0j

Add metadata:
- Key: `state_key` → Value: `tennessee`
- Key: `county_key` → Value: `nashville`

#### Chattanooga Payment Link
**URL**: https://buy.stripe.com/8x29AVaXCeKL86612D63K0k

Add metadata:
- Key: `state_key` → Value: `tennessee`
- Key: `county_key` → Value: `chattanooga`

#### Austin Payment Link
**URL**: https://buy.stripe.com/5kQ4gB1n2dGH4TU26H63K0m

Add metadata:
- Key: `state_key` → Value: `texas`
- Key: `county_key` → Value: `travis`

#### San Antonio Payment Link
**URL**: https://buy.stripe.com/8x26oJd5K1XZ9aah1B63K0l

Add metadata:
- Key: `state_key` → Value: `texas`
- Key: `county_key` → Value: `bexar`

## 3. Configure Webhook

### Development (Testing with Stripe CLI)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:5003/stripe/webhook
```

This will give you a webhook signing secret like `whsec_...`

Set it:
```bash
export STRIPE_WEBHOOK_SECRET='whsec_your_test_secret'
```

### Production

1. Go to **Stripe Dashboard** → **Developers** → **Webhooks**
2. Click **+ Add endpoint**
3. Enter your production URL: `https://yourdomain.com/stripe/webhook`
4. Select these events:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
5. Click **Add endpoint**
6. Copy the **Signing secret** (starts with `whsec_`)
7. Set environment variable:
   ```bash
   export STRIPE_WEBHOOK_SECRET='whsec_your_production_secret'
   ```

## 4. Test the Integration

### Create Test Payment

1. Use Stripe test mode
2. Use test card: `4242 4242 4242 4242`
3. Complete checkout
4. Check your terminal for webhook confirmation:
   ```
   ✅ Subscription created for customer@email.com - tennessee/nashville
   ```

### Verify in Database

```bash
sqlite3 contractor_leads.db "SELECT * FROM subscriptions;"
```

Should show the new subscription!

## Quick Reference

| County | state_key | county_key |
|--------|-----------|------------|
| Nashville | tennessee | nashville |
| Chattanooga | tennessee | chattanooga |
| Austin | texas | travis |
| San Antonio | texas | bexar |

## Troubleshooting

**Webhook not working?**
- Check metadata is exactly as shown above (lowercase, no spaces)
- Verify webhook secret is set correctly
- Check Flask logs for errors
- Test with Stripe CLI first

**Subscription not created?**
- User must exist in database (signup first)
- Email in Stripe must match user email
- Check `/stripe/webhook` endpoint logs

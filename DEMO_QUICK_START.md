# 🚀 OpenRide Demo - Quick Start Guide

## ✅ Zero Configuration Setup

No database installation required! SQLite is built-in.

## 📦 Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 🌱 Step 2: Seed Demo Data

```bash
python seed_demo_data.py
```

This creates:
- ✅ 3 test riders
- ✅ 3 test drivers
- ✅ 3 vehicles
- ✅ 6 active routes
- ✅ SQLite database file (openride_demo.db)

## 🚀 Step 3: Start Backend

```bash
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

## 💻 Step 4: Start Frontend

```bash
cd ../frontend
npm install  # or pnpm install
npm run dev  # or pnpm dev
```

Frontend runs at: `http://localhost:3000`

## 🎯 Demo Accounts

### Rider Login
```
Email: rider@demo.com
Password: demo123
```

### Driver Login
```
Email: driver@demo.com
Password: demo123
```

## 💳 Test Payment

When booking a ride, use this test card:

```
Card Number: 5060990580000217499
CVV: 123
Expiry: 12/26 (any future date)
PIN: 1234
```

## 🧪 Demo Flow

### As Rider:
1. Login with `rider@demo.com` / `demo123`
2. Search route: **Ikeja → VI** at **08:00**
3. See AI-matched results with explanations
4. Book a seat
5. Complete payment with test card
6. Receive blockchain QR token

### As Driver:
1. Login with `driver@demo.com` / `demo123`
2. View your active routes
3. See bookings on your routes
4. Scan rider QR codes (blockchain verification)

## 📍 Test Locations

Popular routes in database:
- Ikeja → VI
- Ogba → Lekki
- Festac → Ikoyi
- Surulere → Yaba
- Lekki → Marina

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Make sure you're in backend folder
cd backend

# Check if database exists
ls openride_demo.db

# If not, run seed script
python seed_demo_data.py
```

### Can't login?
```bash
# Re-run seed script to reset database
python seed_demo_data.py
```

### Payment not working?
- Make sure you see "Loading..." button briefly (Interswitch script loading)
- Check browser console for errors
- Allow popups in your browser
- Use the exact test card details provided

### No routes showing?
```bash
# Re-seed database
python seed_demo_data.py
```

## 📂 Project Structure

```
openride/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── seed_demo_data.py        # Database seeder
│   ├── openride_demo.db         # SQLite database (auto-created)
│   ├── requirements.txt         # Python dependencies
│   └── src/
│       ├── config/              # Settings & database
│       ├── models/              # Database models
│       ├── controllers/         # Business logic
│       ├── routes/              # API endpoints
│       └── utils/               # Blockchain, AI, payments
└── frontend/
    ├── app/                     # Next.js pages
    ├── components/              # React components
    └── package.json             # Node dependencies
```

## 🎬 Demo Presentation Tips

### Highlight These Features:

1. **AI Route Matching**
   - Show explainable AI scores
   - Demonstrate location intelligence
   - Explain multi-factor matching

2. **Blockchain Verification**
   - Show QR code generation
   - Demonstrate token scanning
   - Explain one-time use security

3. **Interswitch Integration**
   - Production-ready payment flow
   - Real Interswitch TEST environment
   - Show transaction reference format

4. **Zero Setup**
   - No database configuration
   - Pre-seeded demo data
   - Instant demo ready

## 🔒 Security Notes

- JWT authentication with 24-hour tokens
- Password hashing with bcrypt
- Blockchain token verification
- One-time use tokens (prevent double booking)
- Payment verification before boarding

## 🎯 For Judges

### Innovation Points:
1. ✅ Multi-factor AI route matching with explanations
2. ✅ Blockchain-based booking verification
3. ✅ Production-ready Interswitch payment integration
4. ✅ Zero-configuration demo setup
5. ✅ Security at multiple layers

### Technical Stack:
- **Backend**: Python FastAPI, SQLAlchemy, SQLite
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Payment**: Interswitch Web Checkout (TEST mode)
- **Auth**: JWT with bcrypt
- **AI**: Custom multi-factor matching algorithm
- **Blockchain**: Cryptographic token verification

## 📱 API Endpoints

- `POST /api/auth/login` - User authentication
- `GET /api/routes/search` - AI-powered route search
- `POST /api/bookings` - Create booking with blockchain token
- `POST /api/payments/initiate` - Initialize Interswitch payment
- `POST /api/payments/verify` - Verify payment status
- `GET /api/bookings/{id}/verify` - Verify blockchain token

Full API docs: `http://localhost:8000/docs`

## 🐛 Known Demo Limitations

- SQLite doesn't support concurrent writes (fine for demo)
- Mock blockchain (not real Polygon network)
- Test card only works in TEST mode
- Limited to Lagos area locations

## 🚀 Production Deployment Notes

To deploy for real use:
1. Switch to PostgreSQL
2. Use LIVE Interswitch credentials
3. Deploy smart contract to Polygon
4. Add real location services (Google Maps)
5. Implement real-time notifications

---

**Demo Ready in 5 Minutes!** 🎉

Need help? Check the detailed guides:
- `IMPLEMENTATION_SUMMARY.md` - Complete features
- `BLOCKCHAIN_GUIDE.md` - Blockchain implementation
- `CHECKLIST.md` - Verification checklist

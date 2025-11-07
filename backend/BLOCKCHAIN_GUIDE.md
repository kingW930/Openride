# Blockchain Verification - Quick Reference Guide

## 📋 Overview
The blockchain verification system prevents double booking and fraud through cryptographic tokens and QR code scanning.

## 🔑 Token Format
```
SEAT-{bookingId}-{hash}
Example: SEAT-abc12345-def67890
```

## 📱 API Endpoints

### 1. Create Booking (with Token Generation)
```http
POST /api/bookings
Authorization: Bearer {jwt_token}

Request Body:
{
  "route_id": "uuid",
  "seats": 2,
  "pickup_stop": "Ogba",
  "dropoff_stop": "VI"
}

Response:
{
  "id": "uuid",
  "blockchain_token": "SEAT-abc12345-def67890",
  "token_data": {
    "tokenId": "SEAT-abc12345-def67890",
    "bookingHash": "sha256_hash...",
    "transactionHash": "0x...",
    "timestamp": 1699123456,
    "blockchainNetwork": "Demo Blockchain",
    "verified": true,
    "expiresAt": 1699209856,
    "qrData": "{\"tokenId\":\"SEAT-...\",\"bookingId\":\"...\",\"timestamp\":...}"
  }
}
```

### 2. Verify Token (Driver Scanning)
```http
GET /api/bookings/{booking_id}/verify

Response:
{
  "booking_id": "uuid",
  "token_id": "SEAT-abc12345-def67890",
  "rider_name": "John Doe",
  "rider_phone": "08012345678",
  "route_info": "Ogba to VI - 08:00 AM",
  "seats_booked": 2,
  "total_amount": 3000.00,
  "status": "confirmed",
  "is_redeemed": false,
  "is_expired": false,
  "qr_data": "{...}",
  "blockchain_token": {...},
  "verified": true,
  "message": "Token valid - rider can board"
}
```

### 3. Redeem Token (After Boarding)
```http
POST /api/bookings/{booking_id}/redeem
Authorization: Bearer {driver_jwt_token}

Response:
{
  "message": "Booking token redeemed successfully",
  "booking_id": "uuid",
  "rider_name": "John Doe",
  "seats_booked": 2,
  "redeemed_at": "2024-11-07T10:30:00"
}
```

## 🎨 Frontend Implementation Guide

### Rider Side - QR Code Display

```typescript
// BookingConfirmation.tsx
import QRCode from 'qrcode.react';

interface TokenData {
  tokenId: string;
  bookingHash: string;
  transactionHash: string;
  timestamp: number;
  blockchainNetwork: string;
  verified: boolean;
  expiresAt: number;
  qrData: string;
}

function BookingToken({ booking }: { booking: BookingWithToken }) {
  const { token_data } = booking;
  
  return (
    <div className="border rounded-lg p-6 space-y-4">
      {/* Blockchain Verified Badge */}
      <div className="flex items-center gap-2 text-green-600">
        <CheckCircle className="w-5 h-5 animate-pulse" />
        <span className="font-semibold">Blockchain Verified</span>
      </div>
      
      {/* Token ID */}
      <div>
        <label className="text-sm text-gray-600">Token ID</label>
        <div className="flex items-center gap-2">
          <code className="text-lg font-mono">{token_data.tokenId}</code>
          <button onClick={() => navigator.clipboard.writeText(token_data.tokenId)}>
            <Copy className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* QR Code */}
      <div className="flex justify-center bg-white p-4 rounded">
        <QRCode 
          value={token_data.qrData}
          size={200}
          level="H"
          includeMargin
        />
      </div>
      
      {/* Security Info */}
      <div className="text-sm text-gray-600 space-y-1">
        <p>✓ One-time use token</p>
        <p>✓ Expires in 24 hours</p>
        <p>✓ Cryptographically secure</p>
        <p>✓ Prevents double booking</p>
      </div>
      
      {/* Blockchain Explorer Link */}
      <a 
        href={`https://demo.openseat.com/explorer/tx/${token_data.transactionHash}`}
        className="text-blue-600 hover:underline text-sm"
        target="_blank"
      >
        View on Blockchain Explorer →
      </a>
      
      {/* Shimmer Effect during Confirmation */}
      {isConfirming && (
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-shimmer" />
      )}
    </div>
  );
}
```

### Driver Side - QR Scanner

```typescript
// QRScanner.tsx
import { QrReader } from 'react-qr-reader';
import { useState } from 'react';

function DriverQRScanner() {
  const [scanning, setScanning] = useState(true);
  const [verificationResult, setVerificationResult] = useState(null);
  
  const handleScan = async (data: string | null) => {
    if (!data) return;
    
    try {
      // Parse QR data
      const qrData = JSON.parse(data);
      const { bookingId } = qrData;
      
      // Verify with backend
      const response = await fetch(`/api/bookings/${bookingId}/verify`);
      const result = await response.json();
      
      setVerificationResult(result);
      setScanning(false);
      
    } catch (error) {
      console.error('QR scan error:', error);
      alert('Invalid QR code');
    }
  };
  
  const handleRedeem = async () => {
    if (!verificationResult) return;
    
    try {
      const response = await fetch(
        `/api/bookings/${verificationResult.booking_id}/redeem`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${driverToken}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      const result = await response.json();
      alert('Booking redeemed successfully!');
      
    } catch (error) {
      console.error('Redeem error:', error);
    }
  };
  
  return (
    <div className="space-y-4">
      {scanning ? (
        <div>
          <h2 className="text-xl font-bold mb-4">Scan Rider QR Code</h2>
          <QrReader
            onResult={(result, error) => {
              if (result) {
                handleScan(result?.getText());
              }
            }}
            constraints={{ facingMode: 'environment' }}
            className="w-full"
          />
        </div>
      ) : verificationResult ? (
        <div className="border rounded-lg p-6 space-y-4">
          {/* Verification Status */}
          <div className={`flex items-center gap-2 ${
            verificationResult.verified ? 'text-green-600' : 'text-red-600'
          }`}>
            {verificationResult.verified ? (
              <CheckCircle className="w-6 h-6" />
            ) : (
              <XCircle className="w-6 h-6" />
            )}
            <span className="font-semibold text-lg">
              {verificationResult.message}
            </span>
          </div>
          
          {/* Rider Details (if valid) */}
          {verificationResult.verified && (
            <>
              <div className="space-y-2">
                <div>
                  <label className="text-sm text-gray-600">Rider</label>
                  <p className="font-semibold">{verificationResult.rider_name}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-600">Phone</label>
                  <p className="font-semibold">{verificationResult.rider_phone}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-600">Seats</label>
                  <p className="font-semibold">{verificationResult.seats_booked}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-600">Amount</label>
                  <p className="font-semibold">₦{verificationResult.total_amount}</p>
                </div>
              </div>
              
              {/* Redeem Button */}
              <button
                onClick={handleRedeem}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold"
                disabled={verificationResult.is_redeemed}
              >
                {verificationResult.is_redeemed ? 'Already Boarded' : 'Confirm Boarding'}
              </button>
            </>
          )}
          
          {/* Scan Another Button */}
          <button
            onClick={() => {
              setScanning(true);
              setVerificationResult(null);
            }}
            className="w-full border py-2 rounded-lg"
          >
            Scan Another Code
          </button>
        </div>
      ) : null}
    </div>
  );
}
```

## 🔒 Security Features

### 1. Token Generation
- **Algorithm**: SHA256 cryptographic hash
- **Uniqueness**: Combines booking ID, route ID, rider ID, amount, timestamp
- **Format**: Human-readable with verification hash

### 2. Validation Checks
```python
# Backend performs these checks:
1. Token format validation (SEAT-{id}-{hash})
2. Booking ID match
3. Hash integrity verification
4. Expiration check (24 hours)
5. Redemption status check
6. Payment confirmation check
7. Driver authorization check
```

### 3. One-Time Use
- Token marked as "redeemed" after boarding
- Database tracks redemption timestamp
- Prevents double boarding with same token

### 4. Expiration
- Tokens valid for 24 hours from creation
- Automatic expiration check on verification
- Clear error message for expired tokens

## 🎯 Error Handling

### Common Errors

#### Token Already Redeemed
```json
{
  "verified": false,
  "is_redeemed": true,
  "message": "Token already redeemed - rider has boarded"
}
```

#### Token Expired
```json
{
  "verified": false,
  "is_expired": true,
  "message": "Token expired - contact support"
}
```

#### Payment Not Confirmed
```json
{
  "verified": false,
  "message": "Payment not confirmed - cannot board"
}
```

#### Invalid Format
```json
{
  "detail": "Invalid token format"
}
```

#### Unauthorized Driver
```json
{
  "detail": "You don't have permission to redeem this booking"
}
```

## 📊 Token Lifecycle

```
1. BOOKING CREATED
   ↓
   Generate Token (SEAT-{id}-{hash})
   ↓
2. TOKEN GENERATED
   Status: PENDING
   Expiry: +24 hours
   ↓
3. PAYMENT CONFIRMED
   Status: CONFIRMED
   Token: ACTIVE
   ↓
4. RIDER ARRIVES
   Driver scans QR
   ↓
5. TOKEN VERIFIED
   Checks: Format ✓ Expiry ✓ Payment ✓ Not redeemed ✓
   ↓
6. RIDER BOARDS
   Driver confirms boarding
   ↓
7. TOKEN REDEEMED
   Status: COMPLETED
   Token: USED (cannot be reused)
```

## 🧪 Testing Flow

### Test Scenario 1: Valid Token
```bash
# 1. Create booking
POST /api/bookings
→ Returns token: SEAT-abc12345-def67890

# 2. Verify token (immediately)
GET /api/bookings/{id}/verify
→ verified: true
→ message: "Token valid - rider can board"

# 3. Redeem token
POST /api/bookings/{id}/redeem
→ Success

# 4. Try to verify again
GET /api/bookings/{id}/verify
→ verified: false
→ is_redeemed: true
→ message: "Token already redeemed - rider has boarded"
```

### Test Scenario 2: Expired Token
```bash
# 1. Create booking 25 hours ago (manual DB update for testing)

# 2. Verify token
GET /api/bookings/{id}/verify
→ verified: false
→ is_expired: true
→ message: "Token expired - contact support"
```

### Test Scenario 3: Unpaid Booking
```bash
# 1. Create booking (payment pending)

# 2. Verify token
GET /api/bookings/{id}/verify
→ verified: false
→ message: "Payment not confirmed - cannot board"
```

## 🚀 Production Considerations

### For Real Blockchain (Polygon)
```solidity
// Smart Contract: BookingVerification.sol
pragma solidity ^0.8.0;

contract BookingVerification {
    struct BookingToken {
        string bookingId;
        address rider;
        uint256 timestamp;
        bool verified;
        bool redeemed;
    }
    
    mapping(string => BookingToken) public tokens;
    
    event TokenMinted(string indexed tokenId, string bookingId, address rider);
    event TokenRedeemed(string indexed tokenId, address driver);
    
    function mintToken(
        string memory tokenId,
        string memory bookingId,
        address rider
    ) public returns (bool) {
        require(tokens[tokenId].timestamp == 0, "Token already exists");
        
        tokens[tokenId] = BookingToken({
            bookingId: bookingId,
            rider: rider,
            timestamp: block.timestamp,
            verified: true,
            redeemed: false
        });
        
        emit TokenMinted(tokenId, bookingId, rider);
        return true;
    }
    
    function redeemToken(string memory tokenId) public returns (bool) {
        require(tokens[tokenId].timestamp > 0, "Token does not exist");
        require(!tokens[tokenId].redeemed, "Token already redeemed");
        require(block.timestamp - tokens[tokenId].timestamp < 86400, "Token expired");
        
        tokens[tokenId].redeemed = true;
        
        emit TokenRedeemed(tokenId, msg.sender);
        return true;
    }
    
    function verifyToken(string memory tokenId) public view returns (
        bool exists,
        bool isValid,
        bool isRedeemed,
        uint256 timestamp
    ) {
        BookingToken memory token = tokens[tokenId];
        exists = token.timestamp > 0;
        isValid = exists && !token.redeemed && (block.timestamp - token.timestamp < 86400);
        isRedeemed = token.redeemed;
        timestamp = token.timestamp;
    }
}
```

### Python Integration with Web3
```python
# Update blockchain.py for production
from web3 import Web3
from eth_account import Account

# Connect to Polygon Mumbai
w3 = Web3(Web3.HTTPProvider(
    'https://rpc-mumbai.maticvigil.com/'
))

CONTRACT_ADDRESS = '0x...'  # Deployed contract
CONTRACT_ABI = [...]  # Contract ABI

def mint_token_on_chain(token_id, booking_id, rider_address):
    """Mint NFT token on Polygon blockchain"""
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    # Build transaction
    tx = contract.functions.mintToken(
        token_id,
        booking_id,
        rider_address
    ).build_transaction({
        'from': DRIVER_ADDRESS,
        'nonce': w3.eth.get_transaction_count(DRIVER_ADDRESS),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return {
        'transactionHash': receipt['transactionHash'].hex(),
        'blockNumber': receipt['blockNumber'],
        'status': 'success' if receipt['status'] == 1 else 'failed'
    }
```

## 📚 Additional Resources

### Libraries for Frontend
```bash
npm install qrcode.react react-qr-reader
```

### Dependencies for Backend
```bash
# Already included in requirements.txt
# For production blockchain:
pip install web3 eth-account
```

### Documentation Links
- QR Code generation: https://github.com/zpao/qrcode.react
- QR Code scanning: https://github.com/react-qr-reader/react-qr-reader
- Web3.py: https://web3py.readthedocs.io/
- Polygon Mumbai: https://mumbai.polygonscan.com/

---
**Built for OpenSeat** | **Secure • Scalable • Demo-Ready**

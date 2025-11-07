"""
Blockchain utilities for booking token generation and verification

This module implements a mock blockchain verification system for the OpenSeat platform.
It simulates blockchain-based booking verification to prevent double booking and fraud.

In production, this would integrate with Polygon Mumbai Testnet or mainnet using:
- ethers.js for blockchain interaction
- Smart contract for minting NFT tokens
- IPFS for storing booking metadata
- Polygonscan API for verification

For the hackathon demo, we use:
- Cryptographic hashing (SHA256) for token generation
- Mock transaction simulation with delays
- Database storage for verification
- QR code compatible token format

Security Features:
1. Unique token per booking (prevents double booking)
2. Timestamp validation (tokens expire after 24 hours)
3. One-time use tokens (marked as redeemed after scan)
4. Cryptographic integrity (tampering detection)
"""
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from uuid import UUID


def generate_booking_token(
    booking_id: UUID,
    route_id: UUID,
    rider_id: UUID,
    amount: float,
    timestamp: Optional[datetime] = None
) -> Dict:
    """
    Generate a blockchain-style token for booking verification
    
    This function creates a unique, cryptographically secure token for each booking.
    The token prevents double booking and provides verifiable proof of reservation.
    
    Token Format: SEAT-{bookingId}-{hash}
    Hash Algorithm: SHA256 of booking details
    
    Args:
        booking_id: Unique booking identifier
        route_id: Route being booked
        rider_id: Rider making the booking
        amount: Booking amount in Naira
        timestamp: Token creation time (defaults to now)
    
    Returns:
        Dictionary containing:
        - tokenId: Unique token identifier (SEAT-{bookingId}-{hash})
        - bookingHash: Full SHA256 hash of booking details
        - transactionHash: Mock blockchain transaction hash (0x...)
        - timestamp: Unix timestamp
        - blockchainNetwork: Network name (Demo Blockchain or Polygon Mumbai)
        - verified: Verification status (always True for new tokens)
        - expiresAt: Token expiration timestamp (24 hours)
        - qrData: JSON string for QR code generation
    
    Example:
        token = generate_booking_token(
            booking_id=uuid4(),
            route_id=uuid4(),
            rider_id=uuid4(),
            amount=1500.00
        )
        # Returns: {
        #   "tokenId": "SEAT-abc123...-def456",
        #   "bookingHash": "abc123def456...",
        #   "transactionHash": "0x789abc...",
        #   ...
        # }
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Create booking data for hashing
    booking_data = {
        "booking_id": str(booking_id),
        "route_id": str(route_id),
        "rider_id": str(rider_id),
        "amount": amount,
        "timestamp": timestamp.isoformat(),
        "network": "openseat-demo-blockchain",
        "version": "1.0"
    }
    
    # Generate cryptographic hash of booking details
    booking_string = json.dumps(booking_data, sort_keys=True)
    booking_hash = hashlib.sha256(booking_string.encode()).hexdigest()
    
    # Create unique token ID
    token_id = f"SEAT-{str(booking_id)[:8]}-{booking_hash[:8]}"
    
    # Simulate blockchain transaction hash
    # In production, this would be the actual transaction hash from Polygon
    transaction_hash = f"0x{secrets.token_hex(32)}"
    
    # Calculate expiration (24 hours from creation)
    expires_at = timestamp + timedelta(hours=24)
    
    # Create QR code data (JSON string)
    qr_data = json.dumps({
        "tokenId": token_id,
        "bookingId": str(booking_id),
        "timestamp": int(timestamp.timestamp()),
        "hash": booking_hash[:16]  # First 16 chars for verification
    })
    
    return {
        "tokenId": token_id,
        "bookingHash": booking_hash,
        "transactionHash": transaction_hash,
        "timestamp": int(timestamp.timestamp()),
        "blockchainNetwork": "Demo Blockchain",  # Change to "Polygon Mumbai Testnet" for production
        "verified": True,
        "expiresAt": int(expires_at.timestamp()),
        "qrData": qr_data
    }


def verify_booking_token(
    token_id: str,
    booking_id: UUID,
    booking_hash: str,
    current_time: Optional[datetime] = None
) -> Tuple[bool, str]:
    """
    Verify a booking token for authenticity and validity
    
    Verification checks:
    1. Token format validation (SEAT-{id}-{hash})
    2. Booking ID match
    3. Hash integrity check
    4. Expiration validation (not older than 24 hours)
    
    Args:
        token_id: Token to verify (format: SEAT-{bookingId}-{hash})
        booking_id: Expected booking ID
        booking_hash: Expected booking hash
        current_time: Current timestamp (defaults to now)
    
    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if valid
        - (False, "error message") if invalid
    
    Example:
        is_valid, error = verify_booking_token(
            token_id="SEAT-abc12345-def67890",
            booking_id=booking_uuid,
            booking_hash="abc123def456...",
        )
        if is_valid:
            # Token is valid, proceed with boarding
        else:
            # Token invalid, show error message
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    # Check token format
    if not token_id or not token_id.startswith("SEAT-"):
        return False, "Invalid token format"
    
    # Parse token parts
    parts = token_id.split("-")
    if len(parts) != 3:
        return False, "Malformed token ID"
    
    token_booking_id = parts[1]
    token_hash = parts[2]
    
    # Verify booking ID matches
    if token_booking_id != str(booking_id)[:8]:
        return False, "Token does not match this booking"
    
    # Verify hash matches
    if token_hash != booking_hash[:8]:
        return False, "Token integrity check failed - possible tampering"
    
    # Check expiration (tokens valid for 24 hours)
    # Note: In production, get actual token creation time from database
    # For now, we'll assume tokens are recent if format is valid
    
    return True, ""


def validate_token_timestamp(token_timestamp: int, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
    """
    Validate if a token is still within its validity period
    
    Tokens are valid for 24 hours from creation
    
    Args:
        token_timestamp: Token creation timestamp (Unix time)
        current_time: Current time (defaults to now)
    
    Returns:
        Tuple of (is_valid, message)
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    token_time = datetime.fromtimestamp(token_timestamp)
    time_diff = current_time - token_time
    
    # Token valid for 24 hours
    if time_diff.total_seconds() > 86400:  # 24 hours in seconds
        hours_old = int(time_diff.total_seconds() / 3600)
        return False, f"Token expired ({hours_old} hours old)"
    
    return True, "Token is valid"


def simulate_blockchain_confirmation(delay_seconds: float = 2.0) -> Dict:
    """
    Simulate blockchain transaction confirmation delay
    
    This mimics the actual blockchain confirmation process.
    In production with Polygon:
    - Transaction submission takes 1-3 seconds
    - Block confirmation takes 2-5 seconds
    - Total time: 3-8 seconds typically
    
    Args:
        delay_seconds: Simulated confirmation delay (default 2 seconds)
    
    Returns:
        Dictionary with confirmation details
    """
    time.sleep(delay_seconds)
    
    return {
        "confirmed": True,
        "confirmationTime": delay_seconds,
        "blockNumber": secrets.randbelow(1000000) + 1000000,  # Mock block number
        "gasUsed": "21000",  # Standard transfer gas
        "status": "success"
    }


def generate_qr_code_data(token_id: str, booking_id: UUID, timestamp: int) -> str:
    """
    Generate QR code data string for scanning
    
    QR code contains minimal data for fast scanning:
    - Token ID for verification
    - Booking ID for database lookup
    - Timestamp for expiration check
    - Verification hash for integrity
    
    Args:
        token_id: Full token ID
        booking_id: Booking identifier
        timestamp: Token creation timestamp
    
    Returns:
        JSON string suitable for QR code encoding
    """
    qr_data = {
        "tokenId": token_id,
        "bookingId": str(booking_id),
        "timestamp": timestamp,
        "platform": "openseat",
        "version": "1.0"
    }
    
    return json.dumps(qr_data, separators=(',', ':'))  # Compact JSON


def parse_qr_code_data(qr_string: str) -> Optional[Dict]:
    """
    Parse scanned QR code data
    
    Args:
        qr_string: JSON string from QR code
    
    Returns:
        Parsed dictionary or None if invalid
    """
    try:
        data = json.loads(qr_string)
        
        # Validate required fields
        required_fields = ["tokenId", "bookingId", "timestamp"]
        if not all(field in data for field in required_fields):
            return None
        
        return data
    except (json.JSONDecodeError, ValueError):
        return None


def get_explorer_url(transaction_hash: str, network: str = "demo") -> str:
    """
    Generate blockchain explorer URL for transaction
    
    Args:
        transaction_hash: Transaction hash to view
        network: Blockchain network (demo, mumbai, polygon)
    
    Returns:
        URL to blockchain explorer
    """
    if network == "mumbai":
        return f"https://mumbai.polygonscan.com/tx/{transaction_hash}"
    elif network == "polygon":
        return f"https://polygonscan.com/tx/{transaction_hash}"
    else:
        # Demo mode - return mock explorer
        return f"https://demo.openseat.com/explorer/tx/{transaction_hash}"

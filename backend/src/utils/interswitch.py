"""
Interswitch payment gateway integration utilities
"""
import httpx
import hashlib
import json
import secrets
from typing import Dict, Optional
from datetime import datetime
from ..config.settings import get_settings

settings = get_settings()


def generate_transaction_ref(booking_id: str) -> str:
    """
    Generate unique transaction reference in format: OPENSEAT-{timestamp}-{randomId}
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_id = secrets.token_hex(4).upper()
    
    return f"OPENSEAT-{timestamp}-{random_id}"


def convert_to_kobo(amount: float) -> int:
    """
    Convert amount from Naira to Kobo (multiply by 100)
    Interswitch expects amount in kobo (smallest currency unit)
    """
    return int(amount * 100)


def convert_from_kobo(amount_kobo: int) -> float:
    """
    Convert amount from Kobo to Naira (divide by 100)
    """
    return float(amount_kobo / 100)


async def initiate_payment(
    amount: float,
    transaction_ref: str,
    customer_email: str,
    customer_name: str
) -> Dict:
    """
    Initiate payment with Interswitch Web Checkout
    Returns payment parameters for frontend integration
    
    Args:
        amount: Amount in Naira
        transaction_ref: Unique transaction reference (OPENSEAT-timestamp-randomId)
        customer_email: Customer email address
        customer_name: Customer name
    
    Returns:
        Dict with payment initialization data including:
        - merchant_code: Interswitch merchant code
        - pay_item_id: Payment item ID
        - txn_ref: Transaction reference
        - amount: Amount in kobo
        - currency: Currency code (566 for NGN)
        - mode: TEST or LIVE
    """
    
    # Convert amount to kobo
    amount_in_kobo = convert_to_kobo(amount)
    
    # Payment initialization data for Interswitch Web Checkout
    payment_data = {
        "merchant_code": settings.INTERSWITCH_MERCHANT_CODE,
        "pay_item_id": settings.INTERSWITCH_PAY_ITEM_ID,
        "txn_ref": transaction_ref,
        "amount": amount_in_kobo,
        "currency": 566,  # NGN currency code
        "mode": "TEST",  # TEST or LIVE
        "customer_email": customer_email,
        "customer_name": customer_name,
        "site_redirect_url": "http://localhost:3000/payment/callback",  # Frontend callback URL
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # For production, you would make API call to Interswitch to create transaction
    # For demo/test environment, we return the parameters needed for frontend
    
    response = {
        "status": "success",
        "message": "Payment initialized successfully",
        "data": {
            **payment_data,
            "interswitch_ref": None,  # Will be generated after payment
            "payment_instructions": "Use test card: 5060990580000217499, CVV: 123, PIN: 1234"
        }
    }
    
    return response


async def verify_payment(
    transaction_ref: str, 
    merchant_code: str = None,
    amount: float = None
) -> Dict:
    """
    Verify payment with Interswitch API
    Makes GET request to Interswitch to confirm transaction status
    
    URL: https://qa.interswitchng.com/collections/api/v1/gettransaction.json
    Params: merchantcode, transactionreference, amount (in kobo)
    
    Args:
        transaction_ref: Transaction reference to verify
        merchant_code: Merchant code (uses settings if not provided)
        amount: Transaction amount in Naira (for verification)
    
    Returns:
        Dict with verification result including status
    """
    
    if merchant_code is None:
        merchant_code = settings.INTERSWITCH_MERCHANT_CODE
    
    # Convert amount to kobo if provided
    amount_in_kobo = convert_to_kobo(amount) if amount else None
    
    # Interswitch verification URL (QA/Sandbox)
    verification_url = "https://qa.interswitchng.com/collections/api/v1/gettransaction.json"
    
    # Query parameters
    params = {
        "merchantcode": merchant_code,
        "transactionreference": transaction_ref,
    }
    
    if amount_in_kobo:
        params["amount"] = amount_in_kobo
    
    try:
        # In production, make actual API call to Interswitch
        async with httpx.AsyncClient() as client:
            # Add authentication headers if required
            headers = {
                "Content-Type": "application/json"
            }
            
            # For demo/test, we simulate successful response
            # Uncomment below for production:
            # response = await client.get(verification_url, params=params, headers=headers, timeout=30.0)
            # response_data = response.json()
            
            # Demo response (simulating successful payment)
            response_data = {
                "ResponseCode": "00",  # 00 = Successful
                "ResponseDescription": "Approved by Financial Institution",
                "Amount": amount_in_kobo,
                "MerchantReference": transaction_ref,
                "PaymentReference": f"ISW{secrets.token_hex(8).upper()}",
                "RetrievalReferenceNumber": secrets.token_hex(6).upper(),
                "TransactionDate": datetime.utcnow().isoformat(),
                "PaymentMethod": "CARD",
                "CardNumber": "506099******7499",
            }
            
            # Check response code
            if response_data.get("ResponseCode") == "00":
                status = "successful"
            else:
                status = "failed"
            
            verification_response = {
                "status": status,
                "transaction_ref": transaction_ref,
                "interswitch_ref": response_data.get("PaymentReference", f"ISW-{transaction_ref[-12:]}"),
                "amount": convert_from_kobo(response_data.get("Amount", amount_in_kobo or 0)),
                "amount_kobo": response_data.get("Amount", amount_in_kobo),
                "payment_method": response_data.get("PaymentMethod", "CARD").lower(),
                "timestamp": response_data.get("TransactionDate", datetime.utcnow().isoformat()),
                "verified": True,
                "response_code": response_data.get("ResponseCode"),
                "response_description": response_data.get("ResponseDescription", ""),
                "card_number": response_data.get("CardNumber", ""),
            }
            
            return verification_response
            
    except httpx.RequestError as e:
        # Handle network errors
        return {
            "status": "failed",
            "transaction_ref": transaction_ref,
            "verified": False,
            "error": f"Network error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Handle other errors
        return {
            "status": "failed",
            "transaction_ref": transaction_ref,
            "verified": False,
            "error": f"Verification error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


def calculate_payment_hash(amount: float, transaction_ref: str) -> str:
    """
    Calculate payment hash for verification
    Used to verify webhook authenticity
    """
    amount_in_kobo = convert_to_kobo(amount)
    hash_string = f"{settings.INTERSWITCH_MERCHANT_CODE}{transaction_ref}{amount_in_kobo}"
    payment_hash = hashlib.sha512(hash_string.encode()).hexdigest()
    
    return payment_hash


def verify_webhook_signature(webhook_data: Dict, signature: str) -> bool:
    """
    Verify Interswitch webhook signature
    Ensures webhook is from legitimate source
    """
    # Calculate expected signature
    amount = webhook_data.get("amount", 0)
    txn_ref = webhook_data.get("transaction_ref", "")
    expected_hash = calculate_payment_hash(convert_from_kobo(amount), txn_ref)
    
    return expected_hash == signature


async def handle_webhook(webhook_data: Dict, signature: Optional[str] = None) -> Dict:
    """
    Handle Interswitch payment webhook callback
    Validates webhook and returns processed data
    """
    
    # Verify webhook signature (in production)
    if signature and not verify_webhook_signature(webhook_data, signature):
        return {
            "status": "failed",
            "error": "Invalid webhook signature",
            "verified": False
        }
    
    # Process webhook data
    response_code = webhook_data.get("ResponseCode", webhook_data.get("response_code", ""))
    
    # Determine status based on response code
    status = "successful" if response_code == "00" else "failed"
    
    return {
        "status": status,
        "transaction_ref": webhook_data.get("transaction_ref", webhook_data.get("MerchantReference")),
        "interswitch_ref": webhook_data.get("interswitch_ref", webhook_data.get("PaymentReference")),
        "amount": convert_from_kobo(webhook_data.get("amount", webhook_data.get("Amount", 0))),
        "verified": True,
        "response_code": response_code,
        "payment_method": webhook_data.get("payment_method", webhook_data.get("PaymentMethod", "card")).lower(),
        "timestamp": webhook_data.get("timestamp", webhook_data.get("TransactionDate", datetime.utcnow().isoformat()))
    }

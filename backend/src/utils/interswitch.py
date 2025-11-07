"""
Interswitch WebPay Redirect Integration
Redirects users to Interswitch payment page, then back to your site after payment
"""
import httpx
import hashlib
import json
import secrets
from typing import Dict, Optional
from datetime import datetime

# INTERSWITCH SANDBOX CREDENTIALS
MERCHANT_CODE = "MX26070"
PAY_ITEM_ID = "Default_Payable_MX26070"
MAC_KEY = "D3D1D05AFE42AD50818167EAC73C109168A0F108F32645C8B59E897FA930DA44F9230910DAC9E20641823799A107A02068F7BC0F4CC41D2952E249552255710F"

# Interswitch URLs
WEBPAY_URL = "https://qa.interswitchng.com/collections/w/pay"  # Sandbox redirect URL
VERIFY_URL = "https://qa.interswitchng.com/collections/api/v1/gettransaction.json"

# Your application URLs
FRONTEND_BASE_URL = "https://openride.vercel.app" # Your React app URL
SITE_REDIRECT_URL = f"{FRONTEND_BASE_URL}/payment/callback"  # Where Interswitch redirects after payment


def generate_transaction_ref(booking_id: str) -> str:
    """
    Generate unique transaction reference in format: OPENRIDE-{timestamp}-{randomId}
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_id = secrets.token_hex(4).upper()
    
    return f"OPENRIDE-{timestamp}-{random_id}"


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


def generate_mac_hash(txn_ref: str, amount_kobo: int) -> str:
    """
    Generate MAC (Message Authentication Code) for payment security
    
    Formula: SHA512(txn_ref + PAY_ITEM_ID + amount + redirect_url + MAC_KEY)
    """
    # Concatenate parameters in specific order
    mac_string = f"{txn_ref}{PAY_ITEM_ID}{amount_kobo}{SITE_REDIRECT_URL}{MAC_KEY}"
    
    # Generate SHA512 hash
    mac_hash = hashlib.sha512(mac_string.encode('utf-8')).hexdigest()
    
    return mac_hash


async def initiate_payment(
    amount: float,
    transaction_ref: str,
    customer_email: str,
    customer_name: str
) -> Dict:
    """
    Initialize payment and generate redirect URL to Interswitch payment page
    
    Args:
        amount: Amount in Naira
        transaction_ref: Unique transaction reference (OPENRIDE-timestamp-randomId)
        customer_email: Customer email address
        customer_name: Customer name
    
    Returns:
        Dict with:
        - redirect_url: Full URL to redirect user to Interswitch
        - payment_params: All payment parameters
        - transaction_ref: Transaction reference for verification
    """
    
    # Convert amount to kobo
    amount_in_kobo = convert_to_kobo(amount)
    
    # Generate MAC hash for security
    mac_hash = generate_mac_hash(transaction_ref, amount_in_kobo)
    
    # Payment parameters for Interswitch WebPay Redirect
    payment_params = {
        "merchant_code": MERCHANT_CODE,
        "pay_item_id": PAY_ITEM_ID,
        "txn_ref": transaction_ref,
        "amount": amount_in_kobo,
        "currency": "566",  # NGN currency code
        "site_redirect_url": SITE_REDIRECT_URL,
        "hash": mac_hash,
        "cust_id": customer_email,
        "cust_name": customer_name,
        "pay_item_name": "OpenRide Booking Payment",
        "mode": "TEST"  # TEST for sandbox, remove for production
    }
    
    # Build redirect URL with query parameters
    query_params = "&".join([f"{key}={value}" for key, value in payment_params.items()])
    redirect_url = f"{WEBPAY_URL}?{query_params}"
    
    response = {
        "status": "success",
        "message": "Payment initialized successfully",
        "data": {
            "redirect_url": redirect_url,
            "payment_params": payment_params,
            "transaction_ref": transaction_ref,
            "amount": amount,
            "amount_kobo": amount_in_kobo,
            "merchant_code": MERCHANT_CODE,
            "site_redirect_url": SITE_REDIRECT_URL
        }
    }
    
    return response


async def verify_payment(
    transaction_ref: str, 
    amount: float = None
) -> Dict:
    """
    Verify payment with Interswitch API after redirect callback
    
    Makes GET request to Interswitch to confirm transaction status
    URL: https://qa.interswitchng.com/collections/api/v1/gettransaction.json
    
    Args:
        transaction_ref: Transaction reference to verify
        amount: Transaction amount in Naira (for verification)
    
    Returns:
        Dict with verification result including status, amount, references
    """
    
    # Convert amount to kobo if provided
    amount_in_kobo = convert_to_kobo(amount) if amount else None
    
    # Query parameters for verification
    params = {
        "merchantcode": MERCHANT_CODE,
        "transactionreference": transaction_ref,
    }
    
    if amount_in_kobo:
        params["amount"] = amount_in_kobo
    
    # Generate hash for verification request
    hash_string = f"{transaction_ref}{MAC_KEY}"
    request_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "Hash": request_hash
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(VERIFY_URL, params=params, headers=headers)
            response_data = response.json()
            
            # Check response code
            # "00" or "10" means successful payment
            response_code = response_data.get("ResponseCode", "")
            
            if response_code in ["00", "10"]:
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
                "response_code": response_code,
                "response_description": response_data.get("ResponseDescription", ""),
                "card_number": response_data.get("CardNumber", ""),
                "retrieval_ref": response_data.get("RetrievalReferenceNumber", ""),
                "raw_response": response_data
            }
            
            return verification_response
            
    except httpx.RequestError as e:
        return {
            "status": "failed",
            "transaction_ref": transaction_ref,
            "verified": False,
            "error": f"Network error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
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
    hash_string = f"{MERCHANT_CODE}{transaction_ref}{amount_in_kobo}{MAC_KEY}"
    payment_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
    
    return payment_hash


def verify_webhook_signature(webhook_data: Dict, signature: str) -> bool:
    """
    Verify Interswitch webhook signature
    Ensures webhook is from legitimate source
    """
    amount = webhook_data.get("amount", 0)
    txn_ref = webhook_data.get("transaction_ref", "")
    expected_hash = calculate_payment_hash(convert_from_kobo(amount), txn_ref)
    
    return expected_hash == signature


def get_test_cards() -> Dict:
    """
    Get Interswitch sandbox test card details
    """
    return {
        "successful_cards": [
            {
                "type": "Mastercard",
                "card_number": "5060990580000217499",
                "cvv": "111",
                "expiry": "03/50",
                "pin": "1111",
                "description": "Successful transaction"
            },
            {
                "type": "Verve",
                "card_number": "5060990580000217480",
                "cvv": "111",
                "expiry": "03/50",
                "pin": "1111",
                "description": "Successful transaction"
            },
            {
                "type": "Visa",
                "card_number": "4012001037141112",
                "cvv": "111",
                "expiry": "03/50",
                "pin": "1111",
                "description": "Successful transaction"
            }
        ],
        "failed_card": {
            "type": "Test Failed",
            "card_number": "5060990580000217481",
            "cvv": "111",
            "expiry": "03/50",
            "pin": "1111",
            "description": "Failed transaction test"
        }
    }
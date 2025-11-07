"""
Payment schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class PaymentInitiate(BaseModel):
    booking_id: UUID
    amount: float = Field(..., gt=0)
    payment_method: Optional[str] = "card"


class PaymentInitializeResponse(BaseModel):
    """Response for payment initialization with Interswitch parameters"""
    merchant_code: str
    pay_item_id: str
    txn_ref: str
    amount: int  # Amount in kobo
    currency: int  # 566 for NGN
    mode: str  # TEST or LIVE
    customer_email: str
    customer_name: str
    site_redirect_url: str
    payment_instructions: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "merchant_code": "MX007",
                "pay_item_id": "101007",
                "txn_ref": "OPENSEAT-20231107120000-ABC123",
                "amount": 150000,
                "currency": 566,
                "mode": "TEST",
                "customer_email": "user@example.com",
                "customer_name": "John Doe",
                "site_redirect_url": "http://localhost:3000/payment/callback",
                "payment_instructions": "Use test card: 5060990580000217499"
            }
        }


class PaymentVerify(BaseModel):
    transaction_ref: str
    interswitch_ref: Optional[str] = None
    status: str


class PaymentVerifyResponse(BaseModel):
    """Response for payment verification"""
    status: str
    transaction_ref: str
    interswitch_ref: Optional[str]
    amount: float
    amount_kobo: int
    payment_method: str
    verified: bool
    response_code: Optional[str]
    response_description: Optional[str]
    card_number: Optional[str]
    timestamp: str


class PaymentResponse(BaseModel):
    id: UUID
    booking_id: UUID
    amount: float
    transaction_ref: str
    interswitch_ref: Optional[str]
    status: str
    payment_method: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PaymentWebhook(BaseModel):
    transaction_ref: str
    interswitch_ref: str
    amount: int  # Amount in kobo
    status: Optional[str] = None
    ResponseCode: Optional[str] = None
    response_code: Optional[str] = None
    payment_method: Optional[str] = None
    PaymentMethod: Optional[str] = None
    MerchantReference: Optional[str] = None
    PaymentReference: Optional[str] = None


class TestCardInfo(BaseModel):
    """Test card information for development/demo"""
    card_number: str = "5060990580000217499"
    cvv: str = "123"
    expiry: str = "12/26"
    pin: str = "1234"
    instructions: str = "Use these details for testing Interswitch payment"
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_number": "5060990580000217499",
                "cvv": "123",
                "expiry": "12/26",
                "pin": "1234",
                "instructions": "Use these details for testing Interswitch payment"
            }
        }

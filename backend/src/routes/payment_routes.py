"""
Payment processing routes
"""
from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from ..config.database import get_db
from ..schemas.payment_schema import (
    PaymentInitiate, 
    PaymentInitializeResponse,
    PaymentVerifyResponse,
    PaymentResponse, 
    PaymentWebhook,
    TestCardInfo
)
from ..controllers.payment_controller import (
    create_payment,
    verify_payment_transaction,
    handle_payment_webhook,
    get_payment_by_booking,
    get_test_card_info
)
from ..middleware.auth_middleware import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/initiate", status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    payment_data: PaymentInitiate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initialize payment with Interswitch
    
    Returns payment parameters for frontend Interswitch Web Checkout integration:
    - merchant_code: Interswitch merchant code
    - pay_item_id: Payment item ID
    - txn_ref: Unique transaction reference (OPENSEAT-timestamp-randomId)
    - amount: Amount in kobo (Naira * 100)
    - currency: 566 (NGN currency code)
    - mode: TEST or LIVE
    - customer details
    
    Also returns test card information for demo purposes
    """
    return await create_payment(payment_data, current_user, db)


@router.post("/verify", response_model=PaymentVerifyResponse)
async def verify_payment(
    transaction_ref: str,
    db: Session = Depends(get_db)
):
    """
    Verify payment status with Interswitch
    
    Makes GET request to Interswitch API:
    URL: https://qa.interswitchng.com/collections/api/v1/gettransaction.json
    Params: merchantcode, transactionreference, amount
    
    On successful verification:
    - Updates payment status to SUCCESSFUL
    - Updates booking status to CONFIRMED
    - Generates blockchain token for booking
    - Reduces available seats on route
    """
    return await verify_payment_transaction(transaction_ref, db)


@router.post("/webhook")
async def payment_webhook(
    webhook_data: PaymentWebhook,
    x_interswitch_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Interswitch payment webhook callback
    
    Validates webhook signature and processes payment status update
    Response code "00" indicates successful payment
    """
    return await handle_payment_webhook(webhook_data, x_interswitch_signature, db)


@router.get("/booking/{booking_id}", response_model=PaymentResponse)
async def get_booking_payment(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment information for a booking
    """
    return get_payment_by_booking(booking_id, current_user, db)


@router.get("/test-card", response_model=TestCardInfo)
async def get_test_card():
    """
    Get test card information for development and demo
    
    Returns:
    - Card Number: 5060990580000217499
    - CVV: 123
    - Expiry: 12/26 (any future date)
    - PIN: 1234
    """
    return get_test_card_info()

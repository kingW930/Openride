"""
Payment controller for handling payment operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict
from uuid import UUID

from ..models.payment import Payment, PaymentStatus
from ..models.booking import Booking, BookingStatus
from ..models.user import User
from ..schemas.payment_schema import (
    PaymentInitiate, 
    PaymentInitializeResponse,
    PaymentVerify, 
    PaymentVerifyResponse,
    PaymentResponse, 
    PaymentWebhook,
    TestCardInfo
)
from ..middleware.error_handler import NotFoundException, BadRequestException
from ..utils.interswitch import (
    initiate_payment, 
    verify_payment, 
    generate_transaction_ref,
    convert_to_kobo,
    verify_webhook_signature
)
from ..utils.blockchain import generate_booking_token


async def create_payment(payment_data: PaymentInitiate, user: User, db: Session) -> Dict:
    """
    Initialize payment for a booking
    
    Steps:
    1. Verify booking exists and belongs to user
    2. Generate unique transaction reference (OPENSEAT-timestamp-randomId)
    3. Calculate amount in kobo (multiply by 100)
    4. Create payment record in database with PENDING status
    5. Return payment parameters for frontend Interswitch integration
    
    Returns:
        Dict with payment initialization parameters including merchant_code,
        pay_item_id, txn_ref, amount (in kobo), currency, mode
    """
    # Verify booking exists and belongs to user
    booking = db.query(Booking).filter(
        and_(Booking.id == payment_data.booking_id, Booking.rider_id == user.id)
    ).first()
    
    if not booking:
        raise NotFoundException("Booking not found")
    
    # Check if payment already exists and is successful
    existing_payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if existing_payment and existing_payment.status == PaymentStatus.SUCCESSFUL:
        raise BadRequestException("Payment already completed for this booking")
    
    # Verify amount matches booking
    if abs(payment_data.amount - booking.total_amount) > 0.01:
        raise BadRequestException("Payment amount doesn't match booking amount")
    
    # Generate unique transaction reference: OPENSEAT-{timestamp}-{randomId}
    transaction_ref = generate_transaction_ref(str(booking.id))
    
    # Initiate payment with Interswitch
    payment_response = await initiate_payment(
        amount=payment_data.amount,
        transaction_ref=transaction_ref,
        customer_email=user.email,
        customer_name=user.name
    )
    
    # Create or update payment record with PENDING status
    if existing_payment:
        payment = existing_payment
        payment.status = PaymentStatus.PENDING
        payment.transaction_ref = transaction_ref
        payment.amount = payment_data.amount
        payment.payment_method = payment_data.payment_method
    else:
        payment = Payment(
            booking_id=booking.id,
            amount=payment_data.amount,
            transaction_ref=transaction_ref,
            status=PaymentStatus.PENDING,
            payment_method=payment_data.payment_method
        )
        db.add(payment)
    
    # Update booking payment status
    booking.payment_status = "pending"
    
    db.commit()
    db.refresh(payment)
    
    # Return payment parameters for frontend
    return {
        "payment_id": str(payment.id),
        "payment_params": payment_response["data"],
        "booking_id": str(booking.id),
        "test_card": TestCardInfo().dict()
    }


async def verify_payment_transaction(transaction_ref: str, db: Session) -> PaymentVerifyResponse:
    """
    Verify payment with Interswitch
    
    Steps:
    1. Find payment by transaction reference
    2. Make GET request to Interswitch API to confirm transaction
       URL: https://qa.interswitchng.com/collections/api/v1/gettransaction.json
       Params: merchantcode, transactionreference, amount (in kobo)
    3. Update payment status to COMPLETED or FAILED based on response
    4. Update booking status to CONFIRMED on success
    5. Generate blockchain token on successful payment
    6. Reduce available seats on route
    7. Return verification result
    
    Returns:
        PaymentVerifyResponse with status, amounts, references, and verification details
    """
    # Find payment by transaction reference
    payment = db.query(Payment).filter(Payment.transaction_ref == transaction_ref).first()
    
    if not payment:
        raise NotFoundException("Payment not found")
    
    # Get booking
    booking = payment.booking
    
    # Verify with Interswitch API
    verification_response = await verify_payment(
        transaction_ref=transaction_ref,
        amount=payment.amount
    )
    
    # Update payment status based on verification
    if verification_response.get("status") == "successful":
        # Update payment to SUCCESSFUL
        payment.status = PaymentStatus.SUCCESSFUL
        payment.interswitch_ref = verification_response.get("interswitch_ref", payment.interswitch_ref)
        
        # Update booking status to CONFIRMED
        booking.payment_status = "successful"
        booking.status = BookingStatus.CONFIRMED
        
        # Generate blockchain token for booking verification
        if not booking.blockchain_token:
            blockchain_token = generate_booking_token(
                booking.id,
                booking.route_id,
                booking.rider_id,
                booking.seats_booked,
                booking.total_amount
            )
            booking.blockchain_token = blockchain_token
        
        # Reduce available seats on route (if not already done)
        route = booking.route
        if booking.seats_booked <= route.available_seats:
            route.available_seats -= booking.seats_booked
        
    else:
        # Update payment to FAILED
        payment.status = PaymentStatus.FAILED
        booking.payment_status = "failed"
    
    db.commit()
    db.refresh(payment)
    
    # Return verification response
    return PaymentVerifyResponse(**verification_response)


async def handle_payment_webhook(webhook_data: PaymentWebhook, signature: str = None, db: Session = None) -> Dict:
    """
    Handle Interswitch payment webhook callback
    
    Steps:
    1. Validate webhook signature to ensure authenticity
    2. Find payment by transaction reference
    3. Update payment status based on webhook data
    4. Update booking status
    5. Generate blockchain token on success
    6. Reduce available seats
    
    Returns:
        Dict with processing result
    """
    # Extract transaction reference (support multiple field names)
    transaction_ref = webhook_data.transaction_ref or webhook_data.MerchantReference
    
    if not transaction_ref:
        raise BadRequestException("Missing transaction reference in webhook data")
    
    # Find payment by transaction reference
    payment = db.query(Payment).filter(Payment.transaction_ref == transaction_ref).first()
    
    if not payment:
        raise NotFoundException(f"Payment not found for transaction: {transaction_ref}")
    
    # Get response code (support multiple field names)
    response_code = webhook_data.ResponseCode or webhook_data.response_code or ""
    
    # Determine status from response code
    # Response code "00" means successful
    is_successful = response_code == "00"
    
    # Update payment status based on webhook data
    if is_successful:
        payment.status = PaymentStatus.SUCCESSFUL
        payment.interswitch_ref = webhook_data.interswitch_ref or webhook_data.PaymentReference
        
        # Update booking
        booking = payment.booking
        booking.payment_status = "successful"
        booking.status = BookingStatus.CONFIRMED
        
        # Generate blockchain token if not exists
        if not booking.blockchain_token:
            blockchain_token = generate_booking_token(
                booking.id,
                booking.route_id,
                booking.rider_id,
                booking.seats_booked,
                booking.total_amount
            )
            booking.blockchain_token = blockchain_token
        
        # Reduce available seats
        route = booking.route
        if booking.seats_booked <= route.available_seats:
            route.available_seats -= booking.seats_booked
        
        db.commit()
        
        return {
            "message": "Webhook processed successfully - Payment confirmed",
            "transaction_ref": transaction_ref,
            "status": "successful",
            "booking_id": str(booking.id),
            "blockchain_token": booking.blockchain_token
        }
        
    else:
        payment.status = PaymentStatus.FAILED
        booking = payment.booking
        booking.payment_status = "failed"
        
        db.commit()
        
        return {
            "message": "Webhook processed - Payment failed",
            "transaction_ref": transaction_ref,
            "status": "failed",
            "response_code": response_code
        }


def get_payment_by_booking(booking_id: UUID, user: User, db: Session) -> PaymentResponse:
    """
    Get payment information for a booking
    """
    # Verify booking exists and user has access
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise NotFoundException("Booking not found")
    
    # Check permissions
    route = booking.route
    if booking.rider_id != user.id and route.driver_id != user.id:
        raise BadRequestException("You don't have permission to view this payment")
    
    # Get payment
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    
    if not payment:
        raise NotFoundException("Payment not found for this booking")
    
    return PaymentResponse.from_orm(payment)


def get_test_card_info() -> TestCardInfo:
    """
    Get test card information for development/demo
    """
    return TestCardInfo()

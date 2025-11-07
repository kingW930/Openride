'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

const PaymentCallback = () => {
  const [status, setStatus] = useState('verifying'); // verifying, success, failed, error
  const [message, setMessage] = useState('Verifying your payment...');
  const [paymentData, setPaymentData] = useState(null);
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    verifyPayment();
  }, []);

  const verifyPayment = async () => {
    try {
      // Get query parameters from URL      
      const txnRef = searchParams.get('txnref');
      const responseCode = searchParams.get('resp');
      const paymentRef = searchParams.get('payRef');
      
      // Get stored transaction reference from localStorage
      const storedTxnRef = localStorage.getItem('pending_payment_ref');
      const bookingId = localStorage.getItem('pending_booking_id');

      if (!txnRef && !storedTxnRef) {
        setStatus('error');
        setMessage('No transaction reference found. Please try again.');
        return;
      }

      const transactionRef = txnRef || storedTxnRef;

      // Call backend to verify payment with Interswitch
      const response = await axios.post(
        `${API_BASE_URL}/payments/verify`,
        {
          transaction_ref: transactionRef
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      const verificationData = response.data;

      if (verificationData.status === 'successful') {
        setStatus('success');
        setMessage('Payment successful! Your booking has been confirmed.');
        setPaymentData(verificationData);

        // Clear stored data
        localStorage.removeItem('pending_payment_ref');
        localStorage.removeItem('pending_booking_id');

        // Redirect to success page after 3 seconds
        setTimeout(() => {
          router.push(`/booking/${bookingId}/success`);
        }, 3000);
      } else {
        setStatus('failed');
        setMessage(verificationData.response_description || 'Payment verification failed. Please try again.');
        setPaymentData(verificationData);
      }

    } catch (error) {
      console.error('Payment verification error:', error);
      setStatus('error');
      setMessage(error.response?.data?.message || 'An error occurred while verifying your payment.');
    }
  };

  const handleRetry = () => {
    const bookingId = localStorage.getItem('pending_booking_id');
    if (bookingId) {
      router.push(`/payment/${bookingId}`);
    } else {
      router.push('/bookings');
    }
  };

  const handleGoHome = () => {
    localStorage.removeItem('pending_payment_ref');
    localStorage.removeItem('pending_booking_id');
    router.push('/');
  };

  return (
    <div className="callback-container">
      <div className="callback-card">
        {/* Verifying State */}
        {status === 'verifying' && (
          <div className="status-content">
            <div className="spinner"></div>
            <h2>Verifying Payment</h2>
            <p>{message}</p>
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
          </div>
        )}

        {/* Success State */}
        {status === 'success' && (
          <div className="status-content success">
            <div className="icon-circle success-icon">
              <span className="checkmark">✓</span>
            </div>
            <h2>Payment Successful!</h2>
            <p>{message}</p>
            
            {paymentData && (
              <div className="payment-summary">
                <div className="summary-row">
                  <span>Transaction Ref:</span>
                  <strong>{paymentData.transaction_ref}</strong>
                </div>
                <div className="summary-row">
                  <span>Amount Paid:</span>
                  <strong>₦{paymentData.amount?.toLocaleString()}</strong>
                </div>
                <div className="summary-row">
                  <span>Payment Ref:</span>
                  <strong>{paymentData.interswitch_ref}</strong>
                </div>
              </div>
            )}

            <p className="redirect-notice">Redirecting to booking details...</p>
          </div>
        )}

        {/* Failed State */}
        {status === 'failed' && (
          <div className="status-content failed">
            <div className="icon-circle failed-icon">
              <span className="cross">✕</span>
            </div>
            <h2>Payment Failed</h2>
            <p>{message}</p>
            
            {paymentData && (
              <div className="payment-summary">
                <div className="summary-row">
                  <span>Transaction Ref:</span>
                  <strong>{paymentData.transaction_ref}</strong>
                </div>
                <div className="summary-row">
                  <span>Response Code:</span>
                  <strong>{paymentData.response_code}</strong>
                </div>
              </div>
            )}

            <div className="action-buttons">
              <button onClick={handleRetry} className="btn btn-primary">
                Try Again
              </button>
              <button onClick={handleGoHome} className="btn btn-secondary">
                Go to Home
              </button>
            </div>
          </div>
        )}

        {/* Error State */}
        {status === 'error' && (
          <div className="status-content error">
            <div className="icon-circle error-icon">
              <span className="exclamation">!</span>
            </div>
            <h2>Verification Error</h2>
            <p>{message}</p>

            <div className="action-buttons">
              <button onClick={handleRetry} className="btn btn-primary">
                Try Again
              </button>
              <button onClick={handleGoHome} className="btn btn-secondary">
                Go to Home
              </button>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .callback-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .callback-card {
          background: white;
          border-radius: 16px;
          padding: 48px;
          max-width: 500px;
          width: 100%;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          text-align: center;
        }

        .status-content {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .spinner {
          width: 64px;
          height: 64px;
          border: 4px solid #e2e8f0;
          border-top-color: #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 24px;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .icon-circle {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 24px;
          font-size: 40px;
          font-weight: bold;
        }

        .success-icon {
          background: #c6f6d5;
          color: #22543d;
        }

        .failed-icon {
          background: #fed7d7;
          color: #742a2a;
        }

        .error-icon {
          background: #feebc8;
          color: #7c2d12;
        }

        h2 {
          margin: 0 0 12px;
          font-size: 28px;
          color: #1a202c;
        }

        p {
          color: #718096;
          font-size: 16px;
          margin: 0 0 24px;
          line-height: 1.6;
        }

        .progress-bar {
          width: 100%;
          height: 4px;
          background: #e2e8f0;
          border-radius: 2px;
          overflow: hidden;
          margin-top: 16px;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
          animation: progress 2s ease-in-out infinite;
        }

        @keyframes progress {
          0% { width: 0%; }
          50% { width: 70%; }
          100% { width: 100%; }
        }

        .payment-summary {
          background: #f7fafc;
          border-radius: 12px;
          padding: 20px;
          width: 100%;
          margin: 24px 0;
          text-align: left;
        }

        .summary-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          font-size: 14px;
        }

        .summary-row:last-child {
          margin-bottom: 0;
        }

        .summary-row span {
          color: #718096;
        }

        .summary-row strong {
          color: #2d3748;
          font-family: 'Courier New', monospace;
          font-size: 13px;
        }

        .redirect-notice {
          color: #48bb78;
          font-size: 14px;
          font-weight: 600;
          margin-top: 16px;
        }

        .action-buttons {
          display: flex;
          gap: 12px;
          margin-top: 24px;
          width: 100%;
        }

        .btn {
          flex: 1;
          padding: 14px 24px;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
          background: #e2e8f0;
          color: #2d3748;
        }

        .btn-secondary:hover {
          background: #cbd5e0;
        }
      `}</style>
    </div>
  );
};

export default PaymentCallback;
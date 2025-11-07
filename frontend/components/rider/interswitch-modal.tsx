// @ts-nocheck
"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Copy, CheckCircle, AlertCircle } from "lucide-react"

// Extend window type for Interswitch
declare global {
  interface Window {
    webpayCheckout: (request: any) => void;
  }
}

interface PaymentParams {
  merchant_code: string;
  pay_item_id: string;
  txn_ref: string;
  amount: number;
  currency: number;
  site_redirect_url?: string;
  cust_name?: string;
  cust_email?: string;
  mode: string;
}

interface InterswitchModalProps {
  amount: number;
  bookingId: string;
  paymentParams: PaymentParams | null;
  onClose: () => void;
  onSuccess: (transactionRef: string) => void;
  onError?: (error: string) => void;
}

export default function InterswitchModal({ 
  amount, 
  bookingId,
  paymentParams,
  onClose, 
  onSuccess,
  onError 
}: InterswitchModalProps) {
  const [step, setStep] = useState<"info" | "processing" | "success" | "error">("info")
  const [copied, setCopied] = useState(false)
  const [scriptLoaded, setScriptLoaded] = useState(false)
  const [errorMessage, setErrorMessage] = useState("")

  const testCard = {
    number: "5060 9905 8000 0217 499",
    cvv: "123",
    expiry: "12/26",
    pin: "1234",
  }

  // Load Interswitch inline checkout script
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://newwebpay.qa.interswitchng.com/inline-checkout.js';
    script.async = true;
    script.onload = () => {
      console.log('✅ Interswitch script loaded');
      setScriptLoaded(true);
    };
    script.onerror = () => {
      console.error('❌ Failed to load Interswitch script');
      setErrorMessage('Failed to load payment gateway. Please try again.');
      setStep('error');
    };
    document.body.appendChild(script);

    return () => {
      // Cleanup script on unmount
      document.body.removeChild(script);
    };
  }, []);

  const handlePayment = () => {
    if (!scriptLoaded) {
      setErrorMessage('Payment gateway is still loading. Please wait...');
      return;
    }

    if (!paymentParams) {
      setErrorMessage('Payment parameters not available. Please try again.');
      setStep('error');
      return;
    }

    setStep("processing");

    // Payment callback function
    const paymentCallback = (response: any) => {
      console.log('Interswitch Payment Response:', response);

      // Check response code
      if (response.resp === '00') {
        // Payment successful
        setStep("success");
        
        // Call backend to verify payment
        setTimeout(() => {
          onSuccess(paymentParams.txn_ref);
        }, 2000);
      } else {
        // Payment failed or cancelled
        setStep("error");
        setErrorMessage(
          response.desc || 
          'Payment was not completed. Please try again.'
        );
        
        if (onError) {
          onError(response.desc || 'Payment failed');
        }
      }
    };

    // Prepare Interswitch payment request
    const interswitchRequest = {
      merchant_code: paymentParams.merchant_code,
      pay_item_id: paymentParams.pay_item_id,
      txn_ref: paymentParams.txn_ref,
      amount: paymentParams.amount, // Amount in kobo
      currency: paymentParams.currency, // 566 for NGN
      site_redirect_url: paymentParams.site_redirect_url || window.location.origin,
      cust_name: paymentParams.cust_name,
      cust_email: paymentParams.cust_email,
      mode: paymentParams.mode, // TEST or LIVE
      onComplete: paymentCallback
    };

    console.log('Initiating Interswitch payment:', interswitchRequest);

    // Call Interswitch inline checkout
    try {
      window.webpayCheckout(interswitchRequest);
    } catch (error) {
      console.error('Error initiating payment:', error);
      setStep("error");
      setErrorMessage('Failed to initiate payment. Please try again.');
      if (onError) {
        onError('Payment initiation failed');
      }
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  };

  const handleRetry = () => {
    setStep("info");
    setErrorMessage("");
  };

  return (
    <Card className="p-6 border border-border">
      {step === "info" && (
        <div className="space-y-6">
          <div>
            <Badge className="bg-blue-500/20 text-blue-700 border-blue-500/30 mb-4">
              {paymentParams?.mode === 'TEST' ? 'Demo Mode' : 'Live Payment'}
            </Badge>
            <h2 className="text-2xl font-bold mb-2">Complete Payment with Interswitch</h2>
            <p className="text-muted-foreground">
              {paymentParams?.mode === 'TEST' 
                ? 'This is a demonstration using Interswitch TEST environment' 
                : 'Secure payment powered by Interswitch'}
            </p>
          </div>

          {/* Amount */}
          <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
            <p className="text-sm text-muted-foreground mb-1">Amount to Pay</p>
            <p className="text-4xl font-bold text-primary">₦{amount.toLocaleString()}</p>
          </div>

          {/* Test Card Info - Only show in TEST mode */}
          {paymentParams?.mode === 'TEST' && (
            <div className="space-y-4">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-blue-500" />
                Test Card Information
              </h3>
              <div className="bg-muted/50 p-4 rounded-lg space-y-3">
                <div className="flex items-center justify-between pb-3 border-b border-border">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Card Number</p>
                    <p className="font-mono text-sm font-semibold">{testCard.number}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => copyToClipboard(testCard.number.replace(/\s/g, ""))}
                    className="gap-2"
                  >
                    <Copy className="w-4 h-4" />
                    {copied ? "Copied!" : "Copy"}
                  </Button>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Expiry Date</p>
                    <p className="font-mono text-sm font-semibold">{testCard.expiry}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">CVV</p>
                    <p className="font-mono text-sm font-semibold">{testCard.cvv}</p>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground mb-1">PIN</p>
                  <p className="font-mono text-sm font-semibold">{testCard.pin}</p>
                </div>
              </div>
            </div>
          )}

          {/* Security Note */}
          <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
            <p className="text-sm text-green-700">
              ✓ Secure connection. Your payment is protected by Interswitch encryption.
            </p>
          </div>

          {/* Transaction Reference */}
          {paymentParams && (
            <div className="text-xs text-muted-foreground">
              <p>Transaction Ref: {paymentParams.txn_ref}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose} className="flex-1 bg-transparent">
              Cancel
            </Button>
            <Button 
              className="bg-primary hover:bg-primary/90 flex-1 gap-2" 
              onClick={handlePayment}
              disabled={!scriptLoaded || !paymentParams}
            >
              {scriptLoaded ? `Pay ₦${amount.toLocaleString()}` : 'Loading...'}
            </Button>
          </div>
        </div>
      )}

      {step === "processing" && (
        <div className="space-y-6 text-center py-12">
          <div className="inline-block">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
          <div>
            <h3 className="text-xl font-bold mb-2">Processing Payment</h3>
            <p className="text-muted-foreground">Please complete payment in the popup window...</p>
            <p className="text-xs text-muted-foreground mt-2">
              If you don't see a popup, please disable your popup blocker
            </p>
          </div>
        </div>
      )}

      {step === "success" && (
        <div className="space-y-6 text-center py-12">
          <div className="inline-block">
            <CheckCircle className="w-16 h-16 text-green-500 animate-bounce" />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-green-600 mb-2">Payment Successful!</h3>
            <p className="text-muted-foreground mb-4">
              Your booking has been confirmed. Generating blockchain token...
            </p>
            {paymentParams && (
              <p className="text-xs text-muted-foreground">
                Transaction Reference: {paymentParams.txn_ref}
              </p>
            )}
          </div>
        </div>
      )}

      {step === "error" && (
        <div className="space-y-6 text-center py-12">
          <div className="inline-block">
            <AlertCircle className="w-16 h-16 text-red-500" />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-red-600 mb-2">Payment Failed</h3>
            <p className="text-muted-foreground mb-4">
              {errorMessage || 'An error occurred during payment. Please try again.'}
            </p>
          </div>
          <div className="flex gap-3 justify-center">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button onClick={handleRetry} className="bg-primary">
              Try Again
            </Button>
          </div>
        </div>
      )}
    </Card>
  )
}

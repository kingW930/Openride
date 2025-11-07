"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useRouter } from "next/navigation"
import BookingConfirmation from "@/components/rider/booking-confirmation"
import InterswitchModal from "@/components/rider/interswitch-modal"
import { ArrowLeft } from "lucide-react"

export default function CheckoutPage() {
  const router = useRouter()
  const [step, setStep] = useState<"review" | "payment" | "confirmation">("review")
  const [bookingData, setBookingData] = useState({
    from: "Ogba",
    to: "VI",
    driverName: "Chidi O.",
    departureTime: "6:30 AM",
    seats: 1,
    pricePerSeat: 1500,
    totalPrice: 1500,
  })

  const handleProceedToPayment = () => {
    setStep("payment")
  }

  const handlePaymentComplete = (transactionRef: string) => {
    setStep("confirmation")
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-primary hover:text-primary/80 transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>
          <h1 className="text-3xl font-bold">Complete Your Booking</h1>
        </div>
      </div>

      {/* Progress Indicator */}
      <div className="border-b border-border bg-card/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-2 md:gap-8">
            <div
              className={`flex flex-col items-center gap-2 md:gap-4 flex-1 ${step === "review" ? "opacity-100" : "opacity-50"}`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${step === "review" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"}`}
              >
                1
              </div>
              <span className="text-xs font-medium">Review Booking</span>
            </div>
            <div className="hidden md:block flex-1 h-1 bg-muted" />
            <div
              className={`flex flex-col items-center gap-2 md:gap-4 flex-1 ${step !== "review" ? "opacity-100" : "opacity-50"}`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${step === "payment" ? "bg-primary text-primary-foreground" : step === "confirmation" ? "bg-green-500 text-white" : "bg-muted text-foreground"}`}
              >
                {step === "confirmation" ? "✓" : "2"}
              </div>
              <span className="text-xs font-medium">Payment</span>
            </div>
            <div className="hidden md:block flex-1 h-1 bg-muted" />
            <div
              className={`flex flex-col items-center gap-2 md:gap-4 flex-1 ${step === "confirmation" ? "opacity-100" : "opacity-50"}`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${step === "confirmation" ? "bg-green-500 text-white" : "bg-muted text-foreground"}`}
              >
                3
              </div>
              <span className="text-xs font-medium">Confirmation</span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {step === "review" && (
            <div className="space-y-6">
              <Card className="p-6 border border-border">
                <h2 className="text-xl font-bold mb-4">Booking Summary</h2>
                <div className="space-y-4">
                  <div className="flex justify-between pb-4 border-b border-border">
                    <span className="text-muted-foreground">Route</span>
                    <span className="font-semibold">
                      {bookingData.from} → {bookingData.to}
                    </span>
                  </div>
                  <div className="flex justify-between pb-4 border-b border-border">
                    <span className="text-muted-foreground">Driver</span>
                    <span className="font-semibold">{bookingData.driverName}</span>
                  </div>
                  <div className="flex justify-between pb-4 border-b border-border">
                    <span className="text-muted-foreground">Departure</span>
                    <span className="font-semibold">{bookingData.departureTime}</span>
                  </div>
                  <div className="flex justify-between pb-4 border-b border-border">
                    <span className="text-muted-foreground">Number of Seats</span>
                    <span className="font-semibold">{bookingData.seats}</span>
                  </div>
                  <div className="flex justify-between pb-4 border-b border-border">
                    <span className="text-muted-foreground">Price per Seat</span>
                    <span className="font-semibold">₦{bookingData.pricePerSeat.toLocaleString()}</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6 border border-primary/30 bg-primary/5">
                <div className="flex justify-between items-center mb-4">
                  <span className="text-lg font-bold">Total Amount</span>
                  <span className="text-3xl font-bold text-primary">₦{bookingData.totalPrice.toLocaleString()}</span>
                </div>
              </Card>

              <div className="flex gap-3">
                <Button variant="outline" onClick={() => router.back()} className="flex-1">
                  Cancel
                </Button>
                <Button className="bg-primary hover:bg-primary/90 flex-1" onClick={handleProceedToPayment}>
                  Proceed to Payment
                </Button>
              </div>
            </div>
          )}

          {step === "payment" && (
            <InterswitchModal
              amount={bookingData.totalPrice}
              onClose={() => setStep("review")}
              onSuccess={(transactionRef) => handlePaymentComplete(transactionRef)}
            />
          )}

          {step === "confirmation" && <BookingConfirmation bookingData={bookingData} />}
        </div>
      </div>
    </div>
  )
}

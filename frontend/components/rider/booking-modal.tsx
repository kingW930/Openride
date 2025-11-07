"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { X, Minus, Plus } from "lucide-react"

export default function BookingModal({ route, onClose, onConfirm }: any) {
  const [seats, setSeats] = useState(1)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md border border-border">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Confirm Booking</h2>
            <button onClick={onClose} className="p-1 hover:bg-muted rounded-lg transition-colors">
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Route Summary */}
          <div className="bg-muted/50 p-4 rounded-lg mb-6">
            <h3 className="font-bold mb-2">
              {route.from} → {route.to}
            </h3>
            <p className="text-sm text-muted-foreground mb-3">with {route.driverName}</p>
            <div className="space-y-2 text-sm">
              <p>
                <strong>Departure:</strong> {route.departureTime}
              </p>
              <p>
                <strong>Vehicle:</strong> {route.vehicleInfo}
              </p>
            </div>
          </div>

          {/* Seat Selection */}
          <div className="mb-6">
            <label className="block font-semibold mb-3">Number of Seats</label>
            <div className="flex items-center gap-4 justify-center">
              <Button variant="outline" size="sm" onClick={() => setSeats(Math.max(1, seats - 1))}>
                <Minus className="w-4 h-4" />
              </Button>
              <span className="text-2xl font-bold w-8 text-center">{seats}</span>
              <Button variant="outline" size="sm" onClick={() => setSeats(Math.min(route.availableSeats, seats + 1))}>
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground text-center mt-2">{route.availableSeats} seats available</p>
          </div>

          {/* Price Breakdown */}
          <div className="bg-primary/5 p-4 rounded-lg mb-6 border border-primary/20">
            <div className="flex justify-between mb-2 text-sm">
              <span>
                ₦{route.pricePerSeat} × {seats} seat{seats > 1 ? "s" : ""}
              </span>
              <span>₦{(route.pricePerSeat * seats).toLocaleString()}</span>
            </div>
            <div className="border-t border-primary/20 pt-2 flex justify-between font-bold">
              <span>Total:</span>
              <span className="text-primary">₦{(route.pricePerSeat * seats).toLocaleString()}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose} className="flex-1 bg-transparent">
              Cancel
            </Button>
            <Button className="bg-primary hover:bg-primary/90 flex-1" onClick={() => onConfirm(seats)}>
              Proceed to Payment
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

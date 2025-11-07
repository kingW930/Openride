"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Clock, MapPin, Phone, AlertCircle, CheckCircle, Compass } from "lucide-react"
import { useState } from "react"

export default function MyBookings({ bookings }: any) {
  const [expandedBooking, setExpandedBooking] = useState<string | null>(null)

  if (bookings.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground mb-6">No bookings yet. Search and book a ride to get started!</p>
        <Button className="bg-primary hover:bg-primary/90">Find a Ride</Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Upcoming Bookings */}
      <div>
        <h2 className="text-xl font-bold mb-4">Upcoming Trips</h2>
        <div className="space-y-4">
          {bookings
            .filter((b) => b.status === "Confirmed")
            .map((booking) => (
              <Card key={booking.id} className="p-6 border border-border">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-lg font-bold">
                        {booking.from} → {booking.to}
                      </h3>
                      <Badge className="bg-green-500/20 text-green-700 border-green-500/30 gap-1">
                        <CheckCircle className="w-3 h-3" />
                        Confirmed
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">with {booking.driverName}</p>
                  </div>
                  <p className="text-2xl font-bold text-primary">₦{booking.totalPrice.toLocaleString()}</p>
                </div>

                {/* Details */}
                <div className="grid md:grid-cols-3 gap-4 mb-4 p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-primary" />
                    <div>
                      <p className="text-xs text-muted-foreground">Departure</p>
                      <p className="font-semibold">{booking.departureTime}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-primary" />
                    <div>
                      <p className="text-xs text-muted-foreground">Seats</p>
                      <p className="font-semibold">{booking.seats}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Booking ID</p>
                    <p className="font-semibold text-primary">{booking.id}</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    className="flex-1 gap-2 bg-transparent"
                    onClick={() => setExpandedBooking(expandedBooking === booking.id ? null : booking.id)}
                  >
                    <Compass className="w-4 h-4" />
                    View Details
                  </Button>
                  <Button variant="outline" className="flex-1 gap-2 bg-transparent">
                    <Phone className="w-4 h-4" />
                    Contact Driver
                  </Button>
                </div>

                {/* Expanded Details */}
                {expandedBooking === booking.id && (
                  <div className="mt-4 p-4 border-t border-border space-y-3">
                    <div className="text-sm">
                      <p className="text-muted-foreground mb-1">Pickup Location</p>
                      <p className="font-semibold">{booking.from} Bus Stop</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-muted-foreground mb-1">Dropoff Location</p>
                      <p className="font-semibold">{booking.to} Bus Stop</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-muted-foreground mb-1">Driver Phone</p>
                      <p className="font-semibold">+234 810 123 4567</p>
                    </div>
                  </div>
                )}
              </Card>
            ))}
        </div>
      </div>

      {/* Past Trips */}
      {bookings.filter((b) => b.status !== "Confirmed").length > 0 && (
        <div>
          <h2 className="text-xl font-bold mb-4 mt-8">Past Trips</h2>
          <div className="space-y-2">
            {bookings
              .filter((b) => b.status !== "Confirmed")
              .map((booking) => (
                <Card key={booking.id} className="p-4 border border-border opacity-75">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">
                        {booking.from} → {booking.to}
                      </p>
                      <p className="text-xs text-muted-foreground">{booking.date}</p>
                    </div>
                    <Button variant="outline" size="sm">
                      Rate Trip
                    </Button>
                  </div>
                </Card>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}

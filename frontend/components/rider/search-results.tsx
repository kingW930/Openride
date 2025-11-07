"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Clock, MapPin, Users, Star, AlertCircle, Zap } from "lucide-react"
import { useState } from "react"
import BookingModal from "@/components/rider/booking-modal"
import AIBadgeCard from "@/components/rider/ai-badge-card"

export default function SearchResults({ results, onBook }: any) {
  const [selectedRoute, setSelectedRoute] = useState<any>(null)
  const [showBookingModal, setShowBookingModal] = useState(false)

  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No rides found for your search. Try different times or locations.</p>
      </div>
    )
  }

  return (
    <>
      <div className="space-y-4">
        {results.map((route: any) => (
          <Card
            key={route.id}
            className={`p-6 border transition-all hover:shadow-lg ${
              route.aiScore >= 90
                ? "border-purple-500/50 bg-gradient-to-r from-purple-50/50 to-transparent dark:from-purple-950/20"
                : "border-border hover:border-primary/50"
            }`}
          >
            <div className="flex flex-col md:flex-row gap-6">
              {/* Driver Info */}
              <div className="flex gap-4 min-w-max">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {route.driverName.split(" ")[0][0]}
                  {route.driverName.split(" ")[1][0]}
                </div>
                <div>
                  <h3 className="font-bold text-lg">{route.driverName}</h3>
                  <p className="text-sm text-muted-foreground">{route.vehicleInfo}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-3 h-3 ${i < Math.floor(route.driverRating) ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground"}`}
                      />
                    ))}
                    <span className="text-xs text-muted-foreground">{route.driverRating}</span>
                  </div>
                </div>
              </div>

              {/* Route Details */}
              <div className="flex-1 min-w-0 space-y-3">
                {route.aiScore >= 85 && (
                  <AIBadgeCard
                    score={route.aiScore}
                    reasons={["Same direction ✓", "Optimal pickup point ✓", "Timing matches ✓"]}
                  />
                )}

                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-bold text-lg">
                      {route.from} → {route.to}
                    </h4>
                    {route.aiScore >= 90 && <Zap className="w-4 h-4 text-purple-500 animate-pulse" />}
                  </div>
                  {route.passingStops.length > 0 && (
                    <p className="text-sm text-muted-foreground">via {route.passingStops.join(", ")}</p>
                  )}
                </div>

                <div className="grid grid-cols-4 gap-2 text-sm">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4 text-primary" />
                    <span>{route.departureTime}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4 text-primary" />
                    <span>{route.availableSeats} seats</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4 text-primary" />
                    <span>₦{route.pricePerSeat}</span>
                  </div>
                </div>
              </div>

              {/* CTA Button */}
              <div className="flex flex-col items-end justify-between md:min-w-max">
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">From</p>
                  <p className="text-2xl font-bold text-secondary">₦{route.pricePerSeat}</p>
                </div>
                <Button
                  className={`w-full md:w-auto ${
                    route.aiScore >= 90
                      ? "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                      : "bg-primary hover:bg-primary/90"
                  }`}
                  onClick={() => {
                    setSelectedRoute(route)
                    setShowBookingModal(true)
                  }}
                >
                  Book Seat
                </Button>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-border/50">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-muted-foreground">Capacity</span>
                <span className="text-xs font-semibold">
                  {route.bookings}/{route.bookings + route.availableSeats} seats
                </span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    route.aiScore >= 90
                      ? "bg-gradient-to-r from-purple-500 to-pink-500"
                      : "bg-gradient-to-r from-primary to-secondary"
                  }`}
                  style={{ width: `${(route.bookings / (route.bookings + route.availableSeats)) * 100}%` }}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {selectedRoute && showBookingModal && (
        <BookingModal
          route={selectedRoute}
          onClose={() => setShowBookingModal(false)}
          onConfirm={(seats) => {
            onBook(selectedRoute.id, seats)
            setShowBookingModal(false)
          }}
        />
      )}
    </>
  )
}

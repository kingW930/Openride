"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock, MapPin, Users, MoreVertical, AlertCircle } from "lucide-react"
import { useState } from "react"

export default function ActiveRoutesList({ routes, onUpdateStatus }: any) {
  const [openMenu, setOpenMenu] = useState<string | null>(null)

  if (routes.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No routes yet. Create one to get started!</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {routes.map((route) => (
        <Card key={route.id} className="p-6 border border-border hover:border-primary/50 transition-all">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-lg font-bold">
                  {route.from} → {route.to}
                </h3>
                <Badge
                  className={
                    route.status === "active"
                      ? "bg-green-500"
                      : route.status === "departed"
                        ? "bg-blue-500"
                        : "bg-red-500"
                  }
                >
                  {route.status === "departed" ? "Departed" : route.status === "cancelled" ? "Cancelled" : "Active"}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                {route.passingStops.length > 0 && `via ${route.passingStops.join(", ")}`}
              </p>
            </div>

            {/* Menu */}
            <div className="relative">
              <button
                onClick={() => setOpenMenu(openMenu === route.id ? null : route.id)}
                className="p-2 hover:bg-muted rounded-lg transition-colors"
              >
                <MoreVertical className="w-5 h-5" />
              </button>
              {openMenu === route.id && (
                <div className="absolute right-0 top-full mt-1 bg-card border border-border rounded-lg shadow-lg z-10">
                  {route.status === "active" && (
                    <>
                      <button
                        onClick={() => {
                          onUpdateStatus(route.id, "departed")
                          setOpenMenu(null)
                        }}
                        className="w-full px-4 py-2 text-left hover:bg-muted transition-colors text-sm"
                      >
                        Mark as Departed
                      </button>
                      <button
                        onClick={() => {
                          onUpdateStatus(route.id, "cancelled")
                          setOpenMenu(null)
                        }}
                        className="w-full px-4 py-2 text-left hover:bg-muted transition-colors text-sm border-t border-border text-destructive"
                      >
                        Cancel Route
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid md:grid-cols-4 gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Departure</p>
                <p className="font-semibold">{route.departureTime}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Available / Booked</p>
                <p className="font-semibold">
                  {route.availableSeats} / {route.bookings}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Price per Seat</p>
                <p className="font-semibold">₦{route.pricePerSeat.toLocaleString()}</p>
              </div>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">Potential Earnings</p>
              <p className="font-semibold text-secondary">
                ₦{(route.availableSeats * route.pricePerSeat).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-muted-foreground">Capacity</span>
              <span className="text-xs font-semibold">
                {route.bookings}/{route.bookings + route.availableSeats} seats
              </span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary to-secondary transition-all"
                style={{ width: `${(route.bookings / (route.bookings + route.availableSeats)) * 100}%` }}
              />
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

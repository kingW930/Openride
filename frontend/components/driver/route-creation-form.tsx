"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { ChevronDown } from "lucide-react"

const locations = ["Ogba", "Ikeja", "Lekki", "VI", "Surulere", "Festac", "Marina", "Yaba"]
const busStops = ["Berger", "Ketu", "Obalende", "CMS", "Ajah", "Ikorodu", "Yaba", "Oshodi", "Mushin"]

export default function RouteCreationForm({ onSubmit, onCancel }: any) {
  const [formData, setFormData] = useState({
    from: "",
    to: "",
    passingStops: [],
    departureTime: "06:30",
    availableSeats: 1,
    pricePerSeat: 1500,
  })

  const [fromOpen, setFromOpen] = useState(false)
  const [toOpen, setToOpen] = useState(false)
  const [stopsOpen, setStopsOpen] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.from && formData.to && formData.departureTime) {
      onSubmit(formData)
    }
  }

  const toggleBusStop = (stop: string) => {
    setFormData((prev) => ({
      ...prev,
      passingStops: prev.passingStops.includes(stop)
        ? prev.passingStops.filter((s) => s !== stop)
        : [...prev.passingStops, stop],
    }))
  }

  return (
    <Card className="p-6 bg-card border border-border mb-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <h3 className="text-xl font-bold">Create New Route</h3>

        <div className="grid md:grid-cols-2 gap-6">
          {/* From Location */}
          <div className="space-y-2">
            <Label htmlFor="from">Start Location</Label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setFromOpen(!fromOpen)}
                className="w-full px-4 py-2 border border-border rounded-lg flex justify-between items-center bg-background hover:bg-muted transition-colors"
              >
                <span>{formData.from || "Select location"}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
              {fromOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-10">
                  {locations.map((loc) => (
                    <button
                      key={loc}
                      type="button"
                      onClick={() => {
                        setFormData((prev) => ({ ...prev, from: loc }))
                        setFromOpen(false)
                      }}
                      className="w-full px-4 py-2 hover:bg-muted text-left transition-colors"
                    >
                      {loc}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* To Location */}
          <div className="space-y-2">
            <Label htmlFor="to">Destination</Label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setToOpen(!toOpen)}
                className="w-full px-4 py-2 border border-border rounded-lg flex justify-between items-center bg-background hover:bg-muted transition-colors"
              >
                <span>{formData.to || "Select location"}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
              {toOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-10">
                  {locations.map((loc) => (
                    <button
                      key={loc}
                      type="button"
                      onClick={() => {
                        setFormData((prev) => ({ ...prev, to: loc }))
                        setToOpen(false)
                      }}
                      className="w-full px-4 py-2 hover:bg-muted text-left transition-colors"
                    >
                      {loc}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Departure Time */}
          <div className="space-y-2">
            <Label htmlFor="time">Departure Time</Label>
            <input
              type="time"
              value={formData.departureTime}
              onChange={(e) => setFormData((prev) => ({ ...prev, departureTime: e.target.value }))}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Available Seats */}
          <div className="space-y-2">
            <Label htmlFor="seats">Available Seats</Label>
            <input
              type="number"
              min="1"
              max="4"
              value={formData.availableSeats}
              onChange={(e) => setFormData((prev) => ({ ...prev, availableSeats: Number.parseInt(e.target.value) }))}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Price Per Seat */}
          <div className="space-y-2">
            <Label htmlFor="price">Price per Seat (₦)</Label>
            <input
              type="number"
              min="500"
              value={formData.pricePerSeat}
              onChange={(e) => setFormData((prev) => ({ ...prev, pricePerSeat: Number.parseInt(e.target.value) }))}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* Passing Bus Stops */}
        <div className="space-y-2">
          <Label>Passing Bus Stops</Label>
          <div className="relative">
            <button
              type="button"
              onClick={() => setStopsOpen(!stopsOpen)}
              className="w-full px-4 py-2 border border-border rounded-lg flex justify-between items-center bg-background hover:bg-muted transition-colors text-left"
            >
              <span>{formData.passingStops.length} stops selected</span>
              <ChevronDown className="w-4 h-4" />
            </button>
            {stopsOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-10 p-4">
                <div className="grid grid-cols-2 gap-3">
                  {busStops.map((stop) => (
                    <label key={stop} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.passingStops.includes(stop)}
                        onChange={() => toggleBusStop(stop)}
                        className="w-4 h-4 rounded"
                      />
                      <span className="text-sm">{stop}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
          {formData.passingStops.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {formData.passingStops.map((stop) => (
                <span key={stop} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                  {stop} ×
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-border">
          <Button type="submit" className="bg-primary hover:bg-primary/90 flex-1">
            Create Route
          </Button>
          <Button type="button" variant="outline" onClick={onCancel} className="flex-1 bg-transparent">
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  )
}

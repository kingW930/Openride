"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { ChevronDown, Search } from "lucide-react"

const locations = ["Ogba", "Ikeja", "Lekki", "VI", "Surulere", "Festac", "Marina", "Yaba"]

export default function SearchForm({ onSearch }: any) {
  const [formData, setFormData] = useState({
    from: "",
    to: "",
    timeRange: "06:00-08:00",
  })

  const [fromOpen, setFromOpen] = useState(false)
  const [toOpen, setToOpen] = useState(false)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.from && formData.to) {
      onSearch(formData)
    }
  }

  return (
    <Card className="p-6 bg-card border border-border">
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="grid md:grid-cols-3 gap-4">
          {/* From Location */}
          <div className="space-y-2">
            <Label htmlFor="from">From</Label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setFromOpen(!fromOpen)}
                className="w-full px-4 py-2 border border-border rounded-lg flex justify-between items-center bg-background hover:bg-muted transition-colors text-left"
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
                      className="w-full px-4 py-2 hover:bg-muted text-left transition-colors text-sm"
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
            <Label htmlFor="to">To</Label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setToOpen(!toOpen)}
                className="w-full px-4 py-2 border border-border rounded-lg flex justify-between items-center bg-background hover:bg-muted transition-colors text-left"
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
                      className="w-full px-4 py-2 hover:bg-muted text-left transition-colors text-sm"
                    >
                      {loc}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Time Range */}
          <div className="space-y-2">
            <Label htmlFor="time">Time Range</Label>
            <select
              value={formData.timeRange}
              onChange={(e) => setFormData((prev) => ({ ...prev, timeRange: e.target.value }))}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="06:00-08:00">6:00 - 8:00 AM</option>
              <option value="07:00-09:00">7:00 - 9:00 AM</option>
              <option value="06:00-09:00">6:00 - 9:00 AM</option>
              <option value="05:30-09:00">5:30 - 9:00 AM</option>
            </select>
          </div>
        </div>

        <Button type="submit" className="w-full bg-primary hover:bg-primary/90 gap-2" size="lg">
          <Search className="w-5 h-5" />
          Search Rides
        </Button>
      </form>
    </Card>
  )
}

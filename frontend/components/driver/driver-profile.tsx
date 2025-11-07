"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Shield, Phone, Mail, Car } from "lucide-react"

export default function DriverProfile() {
  return (
    <div className="space-y-6">
      {/* Main Profile Card */}
      <Card className="p-6 border border-border">
        <div className="flex items-start justify-between mb-6">
          <div className="flex gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-bold text-2xl">
              CO
            </div>
            <div>
              <h2 className="text-2xl font-bold">Chidi Okafor</h2>
              <p className="text-muted-foreground">Professional Driver</p>
              <div className="flex gap-2 mt-2">
                <Badge className="bg-green-500/20 text-green-700 border-green-500/30">
                  <Shield className="w-3 h-3 mr-1" />
                  Verified
                </Badge>
                <Badge className="bg-blue-500/20 text-blue-700 border-blue-500/30">Active</Badge>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-primary">4.9</p>
            <div className="flex gap-1 justify-end mt-1">
              {[...Array(5)].map((_, i) => (
                <span key={i} className="text-yellow-400">
                  ★
                </span>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-1">98 ratings</p>
          </div>
        </div>
      </Card>

      {/* Vehicle Details */}
      <Card className="p-6 border border-border">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Car className="w-5 h-5" />
          Vehicle Details
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Plate Number</p>
            <p className="text-lg font-semibold">ABC-123-CD</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Make & Model</p>
            <p className="text-lg font-semibold">Honda Civic 2018</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Color</p>
            <p className="text-lg font-semibold">Silver</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Capacity</p>
            <p className="text-lg font-semibold">4 Passengers</p>
          </div>
        </div>
      </Card>

      {/* Contact Information */}
      <Card className="p-6 border border-border">
        <h3 className="text-lg font-bold mb-4">Contact Information</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Phone className="w-5 h-5 text-primary" />
            <div>
              <p className="text-sm text-muted-foreground">Phone</p>
              <p className="font-semibold">+234 810 123 4567</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-primary" />
            <div>
              <p className="text-sm text-muted-foreground">Email</p>
              <p className="font-semibold">chidi@openride.ng</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button className="bg-primary hover:bg-primary/90 flex-1">Edit Profile</Button>
        <Button variant="outline" className="flex-1 bg-transparent">
          Bank Details
        </Button>
      </div>
    </div>
  )
}

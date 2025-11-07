"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { QRCodeSVG } from "qrcode.react"
import { CheckCircle, Download, Share2, MapPin, Clock, Phone } from "lucide-react"
import { useRef } from "react"

export default function BookingConfirmation({ bookingData }: any) {
  const bookingId = `BK-${Date.now()}`
  const qrRef = useRef(null)

  const handleDownloadQR = () => {
    const qrElement = document.getElementById("qr-code")
    if (qrElement) {
      const image = qrElement.querySelector("canvas")?.toDataURL("image/png")
      if (image) {
        const link = document.createElement("a")
        link.href = image
        link.download = `seat-token-${bookingId}.png`
        link.click()
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Success Banner */}
      <div className="p-6 bg-green-500/10 border border-green-500/30 rounded-lg text-center">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-green-700 mb-2">Booking Confirmed!</h2>
        <p className="text-green-600">Your ride has been successfully reserved</p>
      </div>

      {/* Booking Reference */}
      <Card className="p-6 border border-border bg-gradient-to-br from-primary/5 to-transparent">
        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-2">Booking Reference</p>
          <p className="text-3xl font-bold text-primary font-mono">{bookingId}</p>
          <p className="text-xs text-muted-foreground mt-2">Save this reference for your records</p>
        </div>
      </Card>

      {/* Blockchain Verification */}
      <Card className="p-6 border border-border">
        <h3 className="font-bold mb-4 flex items-center gap-2">
          <Badge className="bg-blue-500/20 text-blue-700 border-blue-500/30">Blockchain Verified</Badge>
        </h3>
        <div className="space-y-4">
          <div className="text-center">
            <div id="qr-code" className="flex justify-center mb-4">
              <QRCodeSVG
                value={JSON.stringify({
                  bookingId,
                  route: `${bookingData.from}-${bookingData.to}`,
                  timestamp: new Date().toISOString(),
                })}
                size={200}
                level="H"
                includeMargin={true}
              />
            </div>
            <p className="text-sm text-muted-foreground mb-4">Scan with driver to verify booking</p>
          </div>
          <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <p className="text-xs text-blue-700">
              <strong>Seat Token ID:</strong>
              <br />
              SEAT-{Date.now()}-{Math.random().toString(36).substr(2, 9).toUpperCase()}
            </p>
            <p className="text-xs text-blue-600 mt-2">Prevents double-booking and ensures seat security</p>
          </div>
        </div>
      </Card>

      {/* Trip Details */}
      <Card className="p-6 border border-border">
        <h3 className="font-bold mb-4">Trip Details</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
            <MapPin className="w-5 h-5 text-primary flex-shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Route</p>
              <p className="font-semibold">
                {bookingData.from} → {bookingData.to}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
            <Clock className="w-5 h-5 text-primary flex-shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Departure Time</p>
              <p className="font-semibold">{bookingData.departureTime}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
            <Phone className="w-5 h-5 text-primary flex-shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Driver Contact</p>
              <p className="font-semibold">+234 810 123 4567</p>
              <p className="text-xs text-muted-foreground">{bookingData.driverName}</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Important Notes */}
      <Card className="p-6 border border-amber-500/30 bg-amber-500/10">
        <h4 className="font-bold text-amber-700 mb-2">Before Your Trip</h4>
        <ul className="space-y-2 text-sm text-amber-700">
          <li>✓ Arrive 5-10 minutes before departure time</li>
          <li>✓ Have your Booking Reference ready</li>
          <li>✓ Contact driver if running late</li>
          <li>✓ Bring valid ID for verification</li>
        </ul>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button variant="outline" className="flex-1 gap-2 bg-transparent" onClick={handleDownloadQR}>
          <Download className="w-4 h-4" />
          Download QR Code
        </Button>
        <Button className="bg-primary hover:bg-primary/90 flex-1 gap-2">
          <Share2 className="w-4 h-4" />
          Share Booking
        </Button>
      </div>

      <Button variant="outline" className="w-full bg-transparent" onClick={() => (window.location.href = "/rider")}>
        Back to Dashboard
      </Button>
    </div>
  )
}

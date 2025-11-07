"use client"

import { Button } from "@/components/ui/button"
import { LogOut, Home, MapPin, Menu, X } from "lucide-react"
import { useState } from "react"
import { useRouter } from "next/navigation"

export default function RiderSidebar({ activeTab, setActiveTab }: any) {
  const router = useRouter()
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems = [
    { id: "search", label: "Search Rides", icon: Home },
    { id: "bookings", label: "My Bookings", icon: MapPin },
  ]

  return (
    <>
      {/* Mobile Menu Toggle */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 hover:bg-muted rounded-lg"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Sidebar */}
      <div
        className={`fixed md:static md:w-64 h-screen bg-card border-r border-border transition-all duration-300 z-40 ${
          mobileOpen ? "left-0 w-64" : "-left-64 md:left-0"
        }`}
      >
        <div className="p-6 space-y-8">
          {/* Logo */}
          <div className="flex items-center gap-2 cursor-pointer mb-8" onClick={() => router.push("/")}>
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">OS</span>
            </div>
            <span className="font-bold text-lg">OpenSeat</span>
          </div>

          {/* Navigation */}
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id)
                    setMobileOpen(false)
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeTab === item.id ? "bg-primary text-primary-foreground" : "hover:bg-muted text-foreground"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              )
            })}
          </nav>

          {/* User Card */}
          <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
            <p className="text-sm font-medium text-foreground mb-2">Amina Hassan</p>
            <p className="text-xs text-muted-foreground mb-4">Rider Member</p>
            <div className="flex gap-2 mb-4">
              <span className="px-2 py-1 bg-green-500/10 text-green-700 text-xs rounded">Verified</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="w-full gap-2 bg-transparent"
              onClick={() => router.push("/")}
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Overlay */}
      {mobileOpen && <div className="fixed inset-0 bg-black/50 md:hidden z-30" onClick={() => setMobileOpen(false)} />}
    </>
  )
}

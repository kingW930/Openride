"use client"

import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { Menu, X } from "lucide-react"
import { useState } from "react"

export default function Navbar() {
  const router = useRouter()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border transition-all duration-300">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <div
          className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity"
          onClick={() => router.push("/")}
        >
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center animate-pulse-subtle">
            <span className="text-white font-bold text-lg">OS</span>
          </div>
          <span className="font-bold text-xl hidden sm:inline">OpenRide</span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {["How it works", "Safety", "Blog"].map((item) => (
            <a key={item} href="#" className="text-sm font-medium hover:text-primary transition-colors duration-300">
              {item}
            </a>
          ))}
        </div>

        {/* Desktop CTA Buttons */}
        <div className="hidden md:flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.push("/rider")}
            className="hover:bg-muted transition-colors duration-300"
          >
            Rider Login
          </Button>
          <Button
            className="bg-primary hover:bg-primary/90 transition-all duration-300 hover:shadow-md"
            onClick={() => router.push("/driver")}
          >
            Driver Dashboard
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden transition-transform duration-300"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-card animate-fade-in-up">
          <div className="container mx-auto px-4 py-4 space-y-4">
            {["How it works", "Safety", "Blog"].map((item) => (
              <a
                key={item}
                href="#"
                className="block py-2 font-medium hover:text-primary transition-colors duration-300"
              >
                {item}
              </a>
            ))}
            <div className="flex flex-col gap-2 pt-4 border-t border-border">
              <Button variant="outline" onClick={() => router.push("/rider")} className="transition-all duration-300">
                Rider Login
              </Button>
              <Button
                className="bg-primary hover:bg-primary/90 w-full transition-all duration-300"
                onClick={() => router.push("/driver")}
              >
                Driver Dashboard
              </Button>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}

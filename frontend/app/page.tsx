"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import RiderSidebar from "@/components/rider/rider-sidebar"
import SearchForm from "@/components/rider/search-form"
import SearchResults from "@/components/rider/search-results"
import MyBookings from "@/components/rider/my-bookings"
import { MapPin, Search } from "lucide-react"

// Sample routes data
const allRoutes = [
  {
    id: "1",
    driverName: "Chidi O.",
    driverRating: 4.9,
    driverPhoto: "",
    vehicleInfo: "Silver Honda Civic",
    from: "Ogba",
    to: "VI",
    passingStops: ["Berger", "Ketu"],
    departureTime: "6:30 AM",
    availableSeats: 3,
    pricePerSeat: 1500,
    aiScore: 95,
    bookings: 2,
  },
  {
    id: "2",
    driverName: "Amara K.",
    driverRating: 4.8,
    driverPhoto: "",
    vehicleInfo: "Black Toyota Camry",
    from: "Ikeja",
    to: "Lekki",
    passingStops: ["Obalende"],
    departureTime: "7:00 AM",
    availableSeats: 2,
    pricePerSeat: 2000,
    aiScore: 88,
    bookings: 1,
  },
  {
    id: "3",
    driverName: "Tunde A.",
    driverRating: 4.7,
    driverPhoto: "",
    vehicleInfo: "Blue Hyundai Elantra",
    from: "Surulere",
    to: "CMS",
    passingStops: ["Yaba", "Oshodi"],
    departureTime: "6:45 AM",
    availableSeats: 4,
    pricePerSeat: 1200,
    aiScore: 92,
    bookings: 0,
  },
  {
    id: "4",
    driverName: "Ngozi M.",
    driverRating: 5.0,
    driverPhoto: "",
    vehicleInfo: "White Mercedes Sedan",
    from: "Festac",
    to: "Marina",
    passingStops: ["Ajah", "Ikorodu"],
    departureTime: "7:15 AM",
    availableSeats: 2,
    pricePerSeat: 1800,
    aiScore: 96,
    bookings: 2,
  },
]

export default function RiderDashboard() {
  const [activeTab, setActiveTab] = useState("search")
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [hasSearched, setHasSearched] = useState(false)
  const [bookings, setBookings] = useState([
    {
      id: "BK001",
      routeId: "1",
      driverName: "Chidi O.",
      from: "Ogba",
      to: "VI",
      departureTime: "6:30 AM",
      status: "Confirmed",
      seats: 1,
      totalPrice: 1500,
      date: "Today",
    },
  ])

  const handleSearch = (searchParams: any) => {
    const { from, to, timeRange } = searchParams

    const filtered = allRoutes.filter((route) => {
      const routeTime = Number.parseInt(route.departureTime.split(":")[0])
      const [startTime, endTime] = timeRange.split("-").map((t: string) => Number.parseInt(t.split(":")[0]))

      return (
        route.from.toLowerCase().includes(from.toLowerCase()) &&
        route.to.toLowerCase().includes(to.toLowerCase()) &&
        routeTime >= startTime &&
        routeTime <= endTime &&
        route.availableSeats > 0
      )
    })

    // Sort by AI match score
    filtered.sort((a, b) => b.aiScore - a.aiScore)

    setSearchResults(filtered)
    setHasSearched(true)
  }

  const handleBooking = (routeId: string, seats: number) => {
    const route = allRoutes.find((r) => r.id === routeId)
    if (route) {
      const newBooking = {
        id: `BK${Date.now()}`,
        routeId,
        driverName: route.driverName,
        from: route.from,
        to: route.to,
        departureTime: route.departureTime,
        status: "Confirmed",
        seats,
        totalPrice: route.pricePerSeat * seats,
        date: "Today",
      }
      setBookings([...bookings, newBooking])
      setActiveTab("bookings")
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar */}
        <RiderSidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Main Content */}
        <div className="flex-1">
          <div className="p-4 md:p-8 max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-foreground mb-2">Find Your Ride</h1>
              <p className="text-muted-foreground">Search, book, and track your rides with AI-powered matching</p>
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full md:w-fit grid-cols-2">
                <TabsTrigger value="search" className="flex items-center gap-2">
                  <Search className="w-4 h-4" />
                  <span className="hidden sm:inline">Search Rides</span>
                </TabsTrigger>
                <TabsTrigger value="bookings" className="flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  <span className="hidden sm:inline">My Bookings</span>
                </TabsTrigger>
              </TabsList>

              {/* Search Tab */}
              <TabsContent value="search" className="space-y-6">
                <SearchForm onSearch={handleSearch} />
                {hasSearched && <SearchResults results={searchResults} onBook={handleBooking} />}
              </TabsContent>

              {/* Bookings Tab */}
              <TabsContent value="bookings" className="space-y-6">
                <MyBookings bookings={bookings} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  )
}

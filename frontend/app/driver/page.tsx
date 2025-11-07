"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import DriverSidebar from "@/components/driver/driver-sidebar"
import RouteCreationForm from "@/components/driver/route-creation-form"
import ActiveRoutesList from "@/components/driver/active-routes-list"
import EarningsDashboard from "@/components/driver/earnings-dashboard"
import DriverProfile from "@/components/driver/driver-profile"
import { Plus } from "lucide-react"

export default function DriverDashboard() {
  const [activeTab, setActiveTab] = useState("routes")
  const [showNewRouteForm, setShowNewRouteForm] = useState(false)
  const [routes, setRoutes] = useState([
    {
      id: "1",
      from: "Ogba",
      to: "VI",
      passingStops: ["Berger", "Ketu"],
      departureTime: "6:30 AM",
      availableSeats: 3,
      pricePerSeat: 1500,
      status: "active",
      bookings: 2,
    },
    {
      id: "2",
      from: "Ikeja",
      to: "Lekki",
      passingStops: ["Obalende"],
      departureTime: "7:00 AM",
      availableSeats: 2,
      pricePerSeat: 2000,
      status: "active",
      bookings: 1,
    },
  ])

  const handleCreateRoute = (newRoute: any) => {
    setRoutes([...routes, { ...newRoute, id: Date.now().toString(), status: "active", bookings: 0 }])
    setShowNewRouteForm(false)
  }

  const handleUpdateRouteStatus = (routeId: string, newStatus: string) => {
    setRoutes(routes.map((r) => (r.id === routeId ? { ...r, status: newStatus } : r)))
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar */}
        <DriverSidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Main Content */}
        <div className="flex-1">
          <div className="p-4 md:p-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-foreground mb-2">Driver Dashboard</h1>
              <p className="text-muted-foreground">Manage your routes, earnings, and profile</p>
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full md:w-fit grid-cols-3">
                <TabsTrigger value="routes">Routes</TabsTrigger>
                <TabsTrigger value="earnings">Earnings</TabsTrigger>
                <TabsTrigger value="profile">Profile</TabsTrigger>
              </TabsList>

              {/* Routes Tab */}
              <TabsContent value="routes" className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold">My Routes</h2>
                  <Button
                    className="bg-primary hover:bg-primary/90 gap-2"
                    onClick={() => setShowNewRouteForm(!showNewRouteForm)}
                  >
                    <Plus className="w-4 h-4" />
                    New Route
                  </Button>
                </div>

                {showNewRouteForm && (
                  <RouteCreationForm onSubmit={handleCreateRoute} onCancel={() => setShowNewRouteForm(false)} />
                )}

                <ActiveRoutesList routes={routes} onUpdateStatus={handleUpdateRouteStatus} />
              </TabsContent>

              {/* Earnings Tab */}
              <TabsContent value="earnings" className="space-y-6">
                <EarningsDashboard routes={routes} />
              </TabsContent>

              {/* Profile Tab */}
              <TabsContent value="profile" className="space-y-6">
                <DriverProfile />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  )
}

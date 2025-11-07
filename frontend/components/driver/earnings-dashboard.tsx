"use client"

import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { TrendingUp, Calendar, Award } from "lucide-react"

export default function EarningsDashboard({ routes }: any) {
  const todayEarnings = routes.reduce((sum: number, r: any) => sum + r.bookings * r.pricePerSeat, 0)
  const totalEarnings = todayEarnings * 5 // Simulated weekly earnings

  const weeklyData = [
    { day: "Mon", earnings: 8000 },
    { day: "Tue", earnings: 12000 },
    { day: "Wed", earnings: 9500 },
    { day: "Thu", earnings: 15000 },
    { day: "Fri", earnings: 18000 },
    { day: "Sat", earnings: 22000 },
    { day: "Sun", earnings: 14000 },
  ]

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="p-6 border border-border bg-gradient-to-br from-primary/10 to-transparent">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-muted-foreground">Today's Earnings</h3>
            <TrendingUp className="w-5 h-5 text-primary" />
          </div>
          <p className="text-3xl font-bold text-primary">₦{todayEarnings.toLocaleString()}</p>
          <p className="text-xs text-muted-foreground mt-2">{routes.length} active routes</p>
        </Card>

        <Card className="p-6 border border-border bg-gradient-to-br from-secondary/10 to-transparent">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-muted-foreground">Weekly Earnings</h3>
            <Calendar className="w-5 h-5 text-secondary" />
          </div>
          <p className="text-3xl font-bold text-secondary">₦{totalEarnings.toLocaleString()}</p>
          <p className="text-xs text-muted-foreground mt-2">7 days</p>
        </Card>

        <Card className="p-6 border border-border">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-muted-foreground">Total Rides Completed</h3>
            <Award className="w-5 h-5 text-primary" />
          </div>
          <p className="text-3xl font-bold">124</p>
          <p className="text-xs text-muted-foreground mt-2">Rating: 4.9/5.0</p>
        </Card>
      </div>

      {/* Charts */}
      <Card className="p-6 border border-border">
        <h3 className="text-lg font-bold mb-6">Weekly Earnings Breakdown</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={weeklyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip contentStyle={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)" }} />
            <Legend />
            <Bar dataKey="earnings" fill="var(--color-primary)" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  )
}

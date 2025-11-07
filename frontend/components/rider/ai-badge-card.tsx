"use client"
import { Badge } from "@/components/ui/badge"
import { Zap, TrendingUp, CheckCircle2 } from "lucide-react"

export default function AIBadgeCard({ score, reasons }: any) {
  if (score < 85) return null

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0 gap-2 animate-pulse">
          <Zap className="w-4 h-4" />
          AI-Powered Match
        </Badge>
        <Badge variant="outline" className="gap-1">
          <TrendingUp className="w-3 h-3" />
          {score}% Match
        </Badge>
      </div>

      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 p-3 rounded-lg border border-purple-500/30">
        <p className="text-xs font-semibold text-purple-900 dark:text-purple-300 mb-2">Why this match:</p>
        <ul className="space-y-1">
          {reasons.map((reason: string, idx: number) => (
            <li key={idx} className="text-xs text-purple-800 dark:text-purple-200 flex items-center gap-2">
              <CheckCircle2 className="w-3 h-3" />
              {reason}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

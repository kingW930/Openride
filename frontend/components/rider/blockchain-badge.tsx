"use client"

import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Shield } from "lucide-react"

export default function BlockchainBadge() {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge className="bg-green-500/20 text-green-700 border-green-500/30 cursor-help gap-1">
            <Shield className="w-3 h-3" />
            Blockchain Verified
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>Unique seat token prevents double-booking</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

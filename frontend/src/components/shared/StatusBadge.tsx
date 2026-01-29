import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type StatusVariant = "beneficiary" | "objective" | "pai" | "absence"

interface StatusBadgeProps {
  status: string
  variant?: StatusVariant
}

const statusColorMap: Record<StatusVariant, Record<string, string>> = {
  beneficiary: {
    active: "bg-green-100 text-green-800 border-green-200",
    paused: "bg-orange-100 text-orange-800 border-orange-200",
    exited: "bg-gray-100 text-gray-800 border-gray-200",
  },
  objective: {
    pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
    in_progress: "bg-blue-100 text-blue-800 border-blue-200",
    achieved: "bg-green-100 text-green-800 border-green-200",
    abandoned: "bg-red-100 text-red-800 border-red-200",
  },
  pai: {
    draft: "bg-gray-100 text-gray-800 border-gray-200",
    active: "bg-green-100 text-green-800 border-green-200",
    closed: "bg-blue-100 text-blue-800 border-blue-200",
  },
  absence: {
    sick: "bg-red-100 text-red-800 border-red-200",
    vacation: "bg-blue-100 text-blue-800 border-blue-200",
    accident: "bg-orange-100 text-orange-800 border-orange-200",
    unauthorized: "bg-red-100 text-red-800 border-red-200",
  },
}

const statusLabelMap: Record<string, string> = {
  // Beneficiary statuses
  active: "Actif",
  paused: "En pause",
  exited: "Sorti",
  // Objective statuses
  pending: "En attente",
  in_progress: "En cours",
  achieved: "Atteint",
  abandoned: "Abandonne",
  // PAI statuses
  draft: "Brouillon",
  closed: "Cloture",
  // Absence statuses
  sick: "Maladie",
  vacation: "Vacances",
  accident: "Accident",
  unauthorized: "Non autorise",
}

function StatusBadge({ status, variant = "beneficiary" }: StatusBadgeProps) {
  const colorClasses =
    statusColorMap[variant]?.[status] ?? "bg-gray-100 text-gray-800 border-gray-200"
  const label = statusLabelMap[status] ?? status

  return (
    <Badge
      variant="outline"
      className={cn("font-medium", colorClasses)}
    >
      {label}
    </Badge>
  )
}

export { StatusBadge }
export type { StatusBadgeProps, StatusVariant }

import * as React from "react"
import { useFormContext } from "react-hook-form"

import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

interface FormFieldProps {
  name: string
  label: string
  required?: boolean
  hint?: string
  children: React.ReactNode
}

function FormField({ name, label, required, hint, children }: FormFieldProps) {
  const {
    formState: { errors },
  } = useFormContext()

  const error = errors[name]
  const errorMessage = error?.message as string | undefined

  return (
    <div className="space-y-2">
      <Label
        htmlFor={name}
        className={cn(error && "text-destructive")}
      >
        {label}
        {required && <span className="ml-1 text-destructive">*</span>}
      </Label>
      {children}
      {hint && !error && (
        <p className="text-sm text-muted-foreground">{hint}</p>
      )}
      {errorMessage && (
        <p className="text-sm text-destructive">{errorMessage}</p>
      )}
    </div>
  )
}

export { FormField }
export type { FormFieldProps }

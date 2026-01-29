import { useFormContext } from "react-hook-form"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

interface FormDatePickerProps {
  name: string
  label: string
  required?: boolean
}

function FormDatePicker({ name, label, required }: FormDatePickerProps) {
  const {
    register,
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
      <Input
        id={name}
        type="date"
        className={cn(error && "border-destructive")}
        {...register(name)}
      />
      {errorMessage && (
        <p className="text-sm text-destructive">{errorMessage}</p>
      )}
    </div>
  )
}

export { FormDatePicker }
export type { FormDatePickerProps }

import { useFormContext, Controller } from "react-hook-form"

import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

interface FormSelectOption {
  value: string
  label: string
}

interface FormSelectProps {
  name: string
  label: string
  options: FormSelectOption[]
  placeholder?: string
  required?: boolean
}

function FormSelect({
  name,
  label,
  options,
  placeholder = "Selectionner...",
  required,
}: FormSelectProps) {
  const {
    control,
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
      <Controller
        name={name}
        control={control}
        render={({ field }) => (
          <Select
            onValueChange={field.onChange}
            value={field.value}
            defaultValue={field.value}
          >
            <SelectTrigger
              id={name}
              className={cn(error && "border-destructive")}
            >
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      />
      {errorMessage && (
        <p className="text-sm text-destructive">{errorMessage}</p>
      )}
    </div>
  )
}

export { FormSelect }
export type { FormSelectProps, FormSelectOption }

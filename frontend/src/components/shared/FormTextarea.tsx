import { useFormContext } from "react-hook-form"

import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

interface FormTextareaProps {
  name: string
  label: string
  maxLength?: number
  rows?: number
  required?: boolean
  placeholder?: string
}

function FormTextarea({
  name,
  label,
  maxLength,
  rows = 4,
  required,
  placeholder,
}: FormTextareaProps) {
  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext()

  const error = errors[name]
  const errorMessage = error?.message as string | undefined
  const value = watch(name) as string | undefined
  const currentLength = value?.length ?? 0

  return (
    <div className="space-y-2">
      <Label
        htmlFor={name}
        className={cn(error && "text-destructive")}
      >
        {label}
        {required && <span className="ml-1 text-destructive">*</span>}
      </Label>
      <Textarea
        id={name}
        rows={rows}
        placeholder={placeholder}
        className={cn(error && "border-destructive")}
        maxLength={maxLength}
        {...register(name)}
      />
      <div className="flex items-center justify-between">
        {errorMessage ? (
          <p className="text-sm text-destructive">{errorMessage}</p>
        ) : (
          <span />
        )}
        {maxLength && (
          <p
            className={cn(
              "text-sm text-muted-foreground",
              currentLength > maxLength * 0.9 && "text-orange-500",
              currentLength >= maxLength && "text-destructive"
            )}
          >
            {currentLength}/{maxLength}
          </p>
        )}
      </div>
    </div>
  )
}

export { FormTextarea }
export type { FormTextareaProps }

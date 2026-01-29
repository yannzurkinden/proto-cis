import * as React from "react"
import { Upload, X, FileText } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface FileUploadProps {
  onFileSelect: (files: File[]) => void
  accept?: string
  maxSize?: number // in MB
  multiple?: boolean
  label?: string
}

function FileUpload({
  onFileSelect,
  accept,
  maxSize = 10,
  multiple = false,
  label = "Deposer des fichiers ici ou cliquer pour selectionner",
}: FileUploadProps) {
  const [isDragOver, setIsDragOver] = React.useState(false)
  const [selectedFiles, setSelectedFiles] = React.useState<File[]>([])
  const [error, setError] = React.useState<string | null>(null)
  const inputRef = React.useRef<HTMLInputElement>(null)

  const maxSizeBytes = maxSize * 1024 * 1024

  const validateFiles = (files: File[]): File[] => {
    setError(null)
    const validFiles: File[] = []

    for (const file of files) {
      if (file.size > maxSizeBytes) {
        setError(
          `Le fichier "${file.name}" depasse la taille maximale de ${maxSize} Mo.`
        )
        continue
      }
      validFiles.push(file)
    }

    return validFiles
  }

  const handleFiles = (files: FileList | null) => {
    if (!files) return
    const fileArray = Array.from(files)
    const validFiles = validateFiles(fileArray)

    if (validFiles.length > 0) {
      const newFiles = multiple
        ? [...selectedFiles, ...validFiles]
        : validFiles.slice(0, 1)
      setSelectedFiles(newFiles)
      onFileSelect(newFiles)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
    if (inputRef.current) {
      inputRef.current.value = ""
    }
  }

  const handleRemoveFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
    onFileSelect(newFiles)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} o`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
  }

  return (
    <div className="space-y-3">
      <div
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors",
          isDragOver
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
        <p className="text-sm text-muted-foreground text-center">{label}</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Taille maximale : {maxSize} Mo
          {accept && ` | Formats : ${accept}`}
        </p>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleInputChange}
          className="hidden"
        />
      </div>

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {selectedFiles.length > 0 && (
        <ul className="space-y-2">
          {selectedFiles.map((file, index) => (
            <li
              key={`${file.name}-${index}`}
              className="flex items-center justify-between rounded-md border bg-muted/50 px-3 py-2"
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                <span className="truncate text-sm">{file.name}</span>
                <span className="shrink-0 text-xs text-muted-foreground">
                  ({formatFileSize(file.size)})
                </span>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-6 w-6 shrink-0"
                onClick={(e) => {
                  e.stopPropagation()
                  handleRemoveFile(index)
                }}
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Supprimer</span>
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export { FileUpload }
export type { FileUploadProps }

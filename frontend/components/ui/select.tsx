import * as React from "react"
import { Check, ChevronDown } from "@/components/icons"

import { cn } from "@/lib/utils"

interface SelectOptionMap {
  [value: string]: React.ReactNode
}

interface SelectContextValue {
  value: string | undefined
  setValue: (value: string) => void
  open: boolean
  setOpen: (open: boolean) => void
  disabled: boolean
  options: SelectOptionMap
  registerOption: (value: string, label: React.ReactNode) => void
}

const SelectContext = React.createContext<SelectContextValue | null>(null)

function useSelectContext(component: string): SelectContextValue {
  const context = React.useContext(SelectContext)
  if (!context) {
    throw new Error(`${component} must be used within <Select>`) // ensures usage
  }
  return context
}

export interface SelectProps {
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  disabled?: boolean
  children: React.ReactNode
}

export function Select({
  value,
  defaultValue,
  onValueChange,
  disabled = false,
  children,
}: SelectProps) {
  const isControlled = value !== undefined
  const [internalValue, setInternalValue] = React.useState(defaultValue)
  const [open, setOpen] = React.useState(false)
  const [options, setOptions] = React.useState<SelectOptionMap>({})
  const rootRef = React.useRef<HTMLDivElement>(null)

  const currentValue = isControlled ? value : internalValue

  const registerOption = React.useCallback(
    (optionValue: string, label: React.ReactNode) => {
      setOptions((prev) => ({ ...prev, [optionValue]: label }))
    },
    []
  )

  const setValue = React.useCallback(
    (nextValue: string) => {
      if (!isControlled) {
        setInternalValue(nextValue)
      }
      onValueChange?.(nextValue)
      setOpen(false)
    },
    [isControlled, onValueChange]
  )

  const contextValue = React.useMemo<SelectContextValue>(
    () => ({
      value: currentValue,
      setValue,
      open,
      setOpen,
      disabled,
      options,
      registerOption,
    }),
    [currentValue, setValue, open, disabled, options, registerOption]
  )

  React.useEffect(() => {
    if (!open) {
      return
    }

    const handleClick = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClick)
    document.addEventListener("keydown", handleKeyDown)

    return () => {
      document.removeEventListener("mousedown", handleClick)
      document.removeEventListener("keydown", handleKeyDown)
    }
  }, [open])

  return (
    <SelectContext.Provider value={contextValue}>
      <div ref={rootRef} className="relative w-full">
        {children}
      </div>
    </SelectContext.Provider>
  )
}

export interface SelectTriggerProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export const SelectTrigger = React.forwardRef<
  HTMLButtonElement,
  SelectTriggerProps
>(({ className, children, ...props }, ref) => {
  const { open, setOpen, disabled } = useSelectContext("SelectTrigger")

  return (
    <button
      ref={ref}
      type="button"
      role="combobox"
      aria-expanded={open}
      aria-haspopup="listbox"
      onClick={() => {
        if (!disabled) {
          setOpen(!open)
        }
      }}
      className={cn(
        "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      disabled={disabled}
      {...props}
    >
      <div className="flex-1 text-left">{children}</div>
      <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
    </button>
  )
})
SelectTrigger.displayName = "SelectTrigger"

export interface SelectValueProps {
  placeholder?: string
  className?: string
}

export const SelectValue = ({ placeholder, className }: SelectValueProps) => {
  const { value, options } = useSelectContext("SelectValue")

  const selectedOption = value ? options[value] : undefined
  const selected = selectedOption ?? (value ?? placeholder)

  return (
    <span className={cn("line-clamp-1", className)}>{selected}</span>
  )
}

export interface SelectContentProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export const SelectContent = React.forwardRef<HTMLDivElement, SelectContentProps>(
  ({ className, children, ...props }, ref) => {
    const { open } = useSelectContext("SelectContent")

    if (!open) {
      return null
    }

    return (
      <div
        ref={ref}
        className={cn(
          "absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-popover text-popover-foreground shadow-md",
          className
        )}
        role="listbox"
        {...props}
      >
        {children}
      </div>
    )
  }
)
SelectContent.displayName = "SelectContent"

export interface SelectItemProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string
}

export const SelectItem = React.forwardRef<HTMLButtonElement, SelectItemProps>(
  ({ className, value, children, disabled, ...props }, ref) => {
    const { value: selectedValue, setValue, registerOption } = useSelectContext(
      "SelectItem"
    )

    React.useEffect(() => {
      registerOption(value, children)
    }, [value, children, registerOption])

    const isSelected = selectedValue === value

    return (
      <button
        ref={ref}
        type="button"
        role="option"
        aria-selected={isSelected}
        onClick={() => {
          if (!disabled) {
            setValue(value)
          }
        }}
        className={cn(
          "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm text-left transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50",
          isSelected && "bg-accent text-accent-foreground",
          className
        )}
        disabled={disabled}
        {...props}
      >
        <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
          {isSelected ? <Check className="h-4 w-4" /> : null}
        </span>
        {children}
      </button>
    )
  }
)
SelectItem.displayName = "SelectItem"

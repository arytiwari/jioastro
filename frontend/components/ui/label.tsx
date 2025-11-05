import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const labelVariants = cva(
  "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
)

export const Label = React.forwardRef<
  HTMLLabelElement,
  React.PropsWithChildren<React.LabelHTMLAttributes<HTMLLabelElement> & VariantProps<typeof labelVariants>>
>(
  ({ className, children, ...props }, ref) => (
    <label ref={ref} className={cn(labelVariants(), className)} {...props}>
      {children}
    </label>
  )
)

Label.displayName = "Label"

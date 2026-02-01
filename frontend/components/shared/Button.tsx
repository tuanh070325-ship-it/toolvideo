import * as React from 'react'
import { cn } from '@/lib/utils'

/**
 * Shared Button Component
 * Simple square button with white theme
 */
export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'default' | 'outline' | 'ghost'
    size?: 'sm' | 'md' | 'lg'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'default', size = 'md', ...props }, ref) => {
        return (
            <button
                className={cn(
                    // Base styles
                    'inline-flex items-center justify-center font-medium transition-colors',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400',
                    'disabled:opacity-50 disabled:pointer-events-none',

                    // Variants
                    variant === 'default' && 'bg-gray-900 text-white hover:bg-gray-800',
                    variant === 'outline' && 'border border-gray-900 hover:bg-gray-50',
                    variant === 'ghost' && 'hover:bg-gray-100',

                    // Sizes
                    size === 'sm' && 'h-9 px-4 text-sm',
                    size === 'md' && 'h-11 px-6',
                    size === 'lg' && 'h-13 px-8 text-lg',

                    className
                )}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = 'Button'

export { Button }

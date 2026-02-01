import * as React from 'react'
import { cn } from '@/lib/utils'

/**
 * Shared Card Component
 * Simple card with border and white background
 */
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> { }

const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    'border border-gray-200 bg-white p-6',
                    className
                )}
                {...props}
            />
        )
    }
)
Card.displayName = 'Card'

const CardHeader = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn('flex flex-col space-y-1.5 pb-4 border-b border-gray-200', className)}
        {...props}
    />
))
CardHeader.displayName = 'CardHeader'

const CardTitle = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
    <h3
        ref={ref}
        className={cn('text-lg font-semibold leading-none tracking-tight', className)}
        {...props}
    />
))
CardTitle.displayName = 'CardTitle'

const CardContent = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div ref={ref} className={cn('pt-4', className)} {...props} />
))
CardContent.displayName = 'CardContent'

export { Card, CardHeader, CardTitle, CardContent }

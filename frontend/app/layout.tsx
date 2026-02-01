import './globals.css'
import type { Metadata } from 'next'
import { Navigation } from '@/components/shared/Navigation'

export const metadata: Metadata = {
    title: 'Video Tool - AI-Powered Video Processing',
    description: 'Professional video processing with AI capabilities',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body>
                <Navigation />
                {children}
            </body>
        </html>
    )
}

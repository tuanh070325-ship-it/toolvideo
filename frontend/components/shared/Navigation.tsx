'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

/**
 * Shared Navigation Component
 */
export function Navigation() {
    const pathname = usePathname()

    const links = [
        { href: '/', label: 'Dashboard' },
        { href: '/tools', label: '🛠️ Công cụ' },
        { href: '/workflows', label: 'Workflows' },
        { href: '/videos', label: 'Videos' },
        { href: '/generation', label: 'AI Generation' },
        { href: 'http://localhost:8000/comfyui', label: 'ComfyUI (Graph)', external: true },
    ]

    return (
        <nav className="border-b border-gray-200 bg-white">
            <div className="max-w-7xl mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="text-xl font-bold">
                            Video Tool
                        </Link>

                        <div className="flex gap-1">
                            {links.map((link) => (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    target={link.external ? "_blank" : undefined}
                                    className={cn(
                                        'px-4 py-2 text-sm font-medium transition-colors',
                                        pathname === link.href || (link.href !== '/' && pathname?.startsWith(link.href))
                                            ? 'bg-gray-900 text-white'
                                            : 'text-gray-600 hover:bg-gray-100'
                                    )}
                                >
                                    {link.label}
                                </Link>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    )
}

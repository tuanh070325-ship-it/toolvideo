import Link from 'next/link'
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'

export default function HomePage() {
    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">
                    Dashboard
                </h1>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Videos Processed</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-4xl font-bold">0</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Workflows</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-4xl font-bold">0</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>AI Generations</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-4xl font-bold">0</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Quick Actions */}
                <div className="mt-8 border-t border-gray-200 pt-8">
                    <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <Link href="/workflows/editor">
                            <Button className="w-full">Create Workflow</Button>
                        </Link>
                        <Link href="/videos">
                            <Button variant="outline" className="w-full">Download Video</Button>
                        </Link>
                        <Link href="/generation">
                            <Button variant="outline" className="w-full">AI Generation</Button>
                        </Link>
                        <Link href="/workflows">
                            <Button variant="ghost" className="w-full">View Workflows</Button>
                        </Link>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="mt-8 border-t border-gray-200 pt-8">
                    <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
                    <div className="border border-gray-200 p-8 text-center text-gray-500">
                        No recent activity
                    </div>
                </div>
            </div>
        </div>
    )
}

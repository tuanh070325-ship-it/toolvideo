import type { Metadata } from 'next';
import { Inter, Syne, Outfit } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const syne = Syne({ subsets: ['latin'], weight: ['700', '800'], variable: '--font-syne' });
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' });

export const metadata: Metadata = {
  title: 'Video Reup AI Factory - AI Video Processing Tool',
  description:
    'Công cụ tự động xử lý, chỉnh sửa và tái đăng video với AI.  Hỗ trợ TikTok, YouTube, Facebook, Instagram, Douyin',
  keywords: 'video, reup, ai, tiktok, youtube, facebook, instagram, douyin, automation',
  authors: [{ name: 'Video Reup AI Factory' }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} ${syne.variable} ${outfit.variable} font-sans bg-gray-950 text-white antialiased selection:bg-purple-500/30`}>
        {children}
        <Toaster position="bottom-right" />
      </body>
    </html>
  );
}
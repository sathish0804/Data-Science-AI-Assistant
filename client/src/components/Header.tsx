"use client"

import { useRouter } from 'next/navigation'

const Header = () => {
    const router = useRouter()
    const handleLogout = () => {
        if (typeof window !== 'undefined') {
            try { localStorage.removeItem('access_token') } catch {}
            // Use full reload to avoid any client-side state causing a flash
            window.location.replace('/login')
        }
    }
    return (
        <header className="relative flex items-center justify-between px-8 py-5 bg-gradient-to-r from-[#4A3F71] to-[#5E507F] z-10">
            <div className="absolute inset-0 bg-[url('/api/placeholder/100/100')] opacity-5 mix-blend-overlay pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

            <div className="flex items-center relative">
                <div className="absolute -left-3 top-1/2 transform -translate-y-1/2 w-1.5 h-6 bg-teal-400 rounded-full opacity-80"></div>
                <span className="font-bold text-white text-xl tracking-tight">Data Science AI Assistant</span>
            </div>

            <div className="flex items-center space-x-1">
                <span className="text-white bg-white/10 text-xs px-4 py-2 font-medium rounded-lg select-none">CHAT</span>
                <a
                    href="/login"
                    onClick={(e) => {
                        try { localStorage.removeItem('access_token') } catch {}
                    }}
                    className="text-white/90 bg-red-500/70 hover:bg-red-500 text-xs px-4 py-2 font-medium rounded-lg transition-all duration-200 cursor-pointer"
                    role="button"
                >
                    LOGOUT
                </a>
            </div>
        </header>
    )
}

export default Header
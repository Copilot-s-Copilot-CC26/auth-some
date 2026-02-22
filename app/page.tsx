"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null)
  const [userData, setUserData] = useState(null)

  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch("/api/validate_session", {
          method: "GET",
          credentials: "include",
        })

        if (!res.ok) {
          setIsLoggedIn(false)
          return
        }

        const data = await res.json()
        setIsLoggedIn(data.valid === true)
        const cleaned = data.user
        delete cleaned.face
        delete cleaned.voice
        setUserData(cleaned)
      } catch {
        setIsLoggedIn(false)
      }
    }

    checkSession()
  }, [])

  if (isLoggedIn === null) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-white">
        Loading...
      </main>
    )
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white px-6">
      <div className="max-w-xl text-center space-y-6">
        <h1 className="text-5xl font-bold tracking-tight">
          auth-some
        </h1>

        <p className="text-zinc-400 text-lg">
          Secure. Simple. Yours.
        </p>

        {!isLoggedIn && (
          <div className="flex justify-center gap-4 pt-6">
            <Link
              href="/login"
              className="rounded-lg bg-white text-black px-6 py-3 font-medium hover:opacity-90 transition"
            >
              Log In
            </Link>

            <Link
              href="/create-account"
              className="rounded-lg border border-white px-6 py-3 font-medium hover:bg-white hover:text-black transition"
            >
              Sign Up
            </Link>
          </div>
        )}

        {isLoggedIn && (
          <pre className="pt-6">
            {JSON.stringify(userData, null, 2)}
          </pre>
        )}
      </div>
    </main>
  )
}
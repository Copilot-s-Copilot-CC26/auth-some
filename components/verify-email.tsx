'use client'

import {useState} from "react";

const VerifyEmail = () => {

  const [email, setEmail] = useState("");
  const [emailSent, setEmailSent] = useState(false);

  const validateEmailText = (email: string): boolean => {
    if (!email) return false

    const emailRegex =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    return emailRegex.test(email.trim())
  }

  const sendEmail = () => {
    fetch("/api/send_verification",
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({"email": email})
      })
  }

  return (
    <>
      <label
        htmlFor="email"
      >
        Email
      </label>
      <div className={`flex flex-row ${validateEmailText(email) ? 'gap-4' : 'gap-0'}`}>
        <input
          type="text"
          id="email"
          name="email"
          className="flex-1"
          onChange={(e) => setEmail(e.target.value)}
        />

        <button
          type="button"
          className={`
            overflow-hidden
            transition-all duration-300 ease-in-out
            ${validateEmailText(email)
                  ? "opacity-100 w-24"
                  : "opacity-0 w-0 !p-0"}
          `}
          onClick={sendEmail}
        >
          Verify
        </button>
      </div>
    </>
  )
}

export default VerifyEmail;
'use client'

import {useState} from "react";
import {Check} from "lucide-react";

const VerifyEmail = ({ setter }: { setter: (arg0: boolean) => void }) => {

  const [email, setEmail] = useState("");
  const [emailSent, setEmailSent] = useState(false);
  const [code, setCode] = useState(0);
  const [verified, setVerified] = useState(false)

  const validateEmailText = (email: string): boolean => {
    if (!email) return false

    const emailRegex =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    return emailRegex.test(email.trim())
  }

  const validateCodeText = (code: number): boolean => {
    if(!code) return false

    const codeRegex = /^\d{6}$/

    return codeRegex.test(String(code))
  }

  const sendEmail = () => {
    fetch("/api/send_email_verification",
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({"email": email})
      }).then((res) => {
        if (res.status == 200) {
          setEmailSent(true);
        }
    })
  }

  const validateCode = () => {
    fetch("/api/verify_email_code",
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({"email": email, "code": code})
      }).then((res) => {
        if (res.status == 200) {
          setVerified(true);
          setter(true);
        }
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
          disabled={emailSent}
          className="flex-1"
          onChange={(e) => setEmail(e.target.value)}
        />

        <button
          type="button"
          disabled={emailSent}
          className={`
            overflow-hidden whitespace-nowrap
            transition-all duration-300 ease-in-out
            ${validateEmailText(email)
                  ? "opacity-100 w-24 min-w-min"
                  : "opacity-0 w-0 !p-0"}
          `}
          onClick={sendEmail}
        >
          Send Verification Email
        </button>
      </div>
      {emailSent && !verified &&
        <>
          <label htmlFor="emailCode">Verification Code</label>
          <div className={`flex flex-row ${validateCodeText(code) ? 'gap-4' : 'gap-0'}`}>
            <input
              type="text"
              id="emailCode"
              name="emailCode"
              className="flex-1"
              onChange={(e) => setCode(parseInt(e.target.value))}
            />

            <button
              type="button"
              className={`
            overflow-hidden
            transition-all duration-300 ease-in-out
            ${validateCodeText(code)
                ? "opacity-100 w-24"
                : "opacity-0 w-0 !p-0"}
          `}
              onClick={validateCode}
            >
              Verify
            </button>
          </div>
        </>
      }
      {verified && <p className="text-green-500 flex items-center"><Check className="inline" />Email Verified</p>}
    </>
  )
}

export default VerifyEmail;
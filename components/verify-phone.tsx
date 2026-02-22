'use client'

import {useState} from "react";
import {Check} from "lucide-react";

const VerifyPhone = () => {

  const [phone, setPhone] = useState("");
  const [textSent, setTextSent] = useState(false);
  const [code, setCode] = useState(0);
  const [verified, setVerified] = useState(false)

  const validatePhoneText = (phoneText: string): boolean => {
    if (!phoneText) return false

    const phoneTextRegex =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    return phoneTextRegex.test(phoneText.trim())
  }

  const validateCodeText = (code: number): boolean => {
    if(!code) return false

    const codeRegex = /^\d{6}$/

    return codeRegex.test(String(code))
  }

  const sendText = () => {
    fetch("/api/send_text_verification",
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({"phone": phone})
      }).then((res) => {
      if (res.status == 200) {
        setTextSent(true);
      }
    })
  }

  const validateCode = () => {
    fetch("/api/verify_code",
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({"phone": phone, "code": code})
      }).then((res) => {
      if (res.status == 200) {
        setVerified(true);
      }
    })
  }

  return (
    <>
      <label
        htmlFor="phone"
      >
        Phone Number
      </label>
      <div className={`flex flex-row ${validatePhoneText(phone) ? 'gap-4' : 'gap-0'}`}>
        <input
          type="text"
          id="phone"
          name="phone"
          disabled={textSent}
          className="flex-1"
          onChange={(e) => setPhone(e.target.value)}
        />

        <button
          type="button"
          disabled={textSent}
          className={`
            overflow-hidden whitespace-nowrap
            transition-all duration-300 ease-in-out
            ${validatePhoneText(phone)
            ? "opacity-100 w-24 min-w-min"
            : "opacity-0 w-0 !p-0"}
          `}
          onClick={sendText}
        >
          Send Verification Text
        </button>
      </div>
      {textSent && !verified &&
        <>
          <label htmlFor="textCode">Verification Code</label>
          <div className={`flex flex-row ${validateCodeText(code) ? 'gap-4' : 'gap-0'}`}>
            <input
              type="text"
              id="textCode"
              name="textCode"
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
      {verified && <p className="text-green-500 flex items-center"><Check className="inline" />Phone Number Verified</p>}
    </>
  )
}

export default VerifyPhone;
'use client'

import TextField from "@/components/textField"
import HCaptcha from "@hcaptcha/react-hcaptcha"
import { useState } from "react"
import dynamic from "next/dynamic"
import WebcamCapture from "@/components/webcam-capture"
import VerifyEmail from "@/components/verify-email"
import VerifyPhone from "@/components/verify-phone"
import FiveSecondRecorder from "@/components/voice-record"
import { X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

const Page = () => {
  const [step, setStep] = useState(0)
  const totalSteps = 7

  const [c1, setC1] = useState<string | null>(null)
  const [c2, setC2] = useState<string | null>(null)

  const [emailVerified, setEmailVerified] = useState(false)
  const [phoneVerified, setPhoneVerified] = useState(false)
  const [face, setFace] = useState<Blob | null>(null)
  const [audio, setAudio] = useState<Blob | null>(null)

  const next = () => setStep((s) => s + 1)
  const back = () => setStep((s) => s - 1)

  const canSubmit =
    emailVerified &&
    phoneVerified &&
    c1 &&
    c2 &&
    face &&
    audio

  const submit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    const formData = new FormData(e.currentTarget)

    // @ts-ignore
    formData.append('email', document.querySelector('[name="email"]').value)
    // @ts-ignore
    formData.append('phone', document.querySelector('[name="phone"]').value)

    // @ts-ignore
    formData.append("image", face, "photo.png")
    // @ts-ignore
    formData.append("voice", audio, "voice.webm")

    fetch("/api/validate_user", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((json) => console.log(json))
  }

  const progress = ((step + 1) / totalSteps) * 100

  return (
    <form
      onSubmit={submit}
      className="flex flex-col items-center p-6"
    >
      <div className="w-1/3">
        <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
          <div
            className="h-full bg-black transition-all duration-300"
            style={{
              width: `${((step + 1) / totalSteps) * 100}%`,
            }}
          />
        </div>
      </div>
      <div className="relative w-1/3 overflow-x-hidden flex flex-col items-center justify-center">
        <motion.div
          animate={{ x: `-${step * 100}%` }}
          transition={{ duration: 0.3 }}
          className="flex w-full"
        >

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What is your email?</p>
            <VerifyEmail setter={setEmailVerified} />
            <button type="button" onClick={next}>Next</button>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What is your phone number?</p>
            <VerifyPhone setter={setPhoneVerified} />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">Username & Password</p>
            <TextField name="Username" />
            <label>Password</label>
            <input type="password" name="password" />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What do you look like?</p>
            <WebcamCapture setter={setFace} />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What do you sound like?</p>
            <FiveSecondRecorder setter={setAudio} />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">Are you a robot?</p>
            <HCaptcha
              sitekey="370c332a-75f8-48c6-9562-d97e0a42f870"
              onVerify={(token) => setC1(token)}
            />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-4">
            <p className="text-lg font-bold">Review & Submit</p>

            {!canSubmit && (
              <div>
                {!emailVerified && <p className="text-red-500 font-bold flex items-center"><X/> Unverified Email</p>}
                {!phoneVerified && <p className="text-red-500 font-bold flex items-center"><X/> Unverified Phone</p>}
                {!face && <p className="text-red-500 font-bold flex items-center"><X/> No Face Photo</p>}
                {!audio && <p className="text-red-500 font-bold flex items-center"><X/> No Voice Recording</p>}
                {!c1 && <p className="text-red-500 font-bold flex items-center"><X/> Incomplete CAPTCHA</p>}
                {!c2 && <p className="text-red-500 font-bold flex items-center"><X/> Final CAPTCHA</p>}
              </div>
            )}

            <HCaptcha
              sitekey="370c332a-75f8-48c6-9562-d97e0a42f870"
              onVerify={(token) => setC2(token)}
            />

            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>

              {canSubmit && (
                <input
                  type="submit"
                  className="px-4 py-2 !bg-green-600 text-white rounded"
                />
              )}
            </div>
          </section>
        </motion.div>
      </div>
    </form>
  )
}

export default Page
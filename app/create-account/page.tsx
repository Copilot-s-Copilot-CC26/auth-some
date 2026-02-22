'use client'

import TextField from "@/components/textField"
import HCaptcha from "@hcaptcha/react-hcaptcha"
import {useState} from "react"
import dynamic from "next/dynamic"
import WebcamCapture from "@/components/webcam-capture"
import VerifyEmail from "@/components/verify-email"
import VerifyPhone from "@/components/verify-phone"
import FiveSecondRecorder from "@/components/voice-record"
import {X} from "lucide-react"
import {motion} from "framer-motion"

const CoordinatePicker = dynamic(
  () => import("@/components/coordinate-picker"),
  {ssr: false}
)

const Page = () => {
  const [step, setStep] = useState(0)

  const [c1, setC1] = useState<string | null>(null)
  const [c2, setC2] = useState<string | null>(null)

  const [emailVerified, setEmailVerified] = useState(false)
  const [phoneVerified, setPhoneVerified] = useState(false)
  const [coords, setCoords] = useState<[number, number] | null>(null)
  const [face, setFace] = useState<Blob | null>(null)
  const [audio, setAudio] = useState<Blob | null>(null)

  const next = () => {
    setStep((s) => s + 1)
  }

  const back = () => {
    setStep((s) => s - 1)
  }

  const totalSteps = 12

  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault()

  const formData = new FormData(e.currentTarget)

  // @ts-ignore
  formData.set("email", document.querySelector('[name="email"]').value)
  // @ts-ignore
  formData.set("phone", document.querySelector('[name="phone"]').value)

  formData.set("sleep-coords", JSON.stringify(coords))

  if (face) {
    // @ts-ignore
    formData.set("image", face, "photo.png")
  }

  if (audio) {
    // @ts-ignore
    formData.set("voice", audio, "voice.webm")
  }

  try {
    const res = await fetch("/api/create_user", {
      method: "POST",
      body: formData,
      credentials: "include",
    })

    if (!res.ok) {
      const data = await res.json()
      console.error(data)
      return alert("Signup failed")
    }

    window.location.href = "/login"

  } catch (err) {
    console.error(err)
    alert("Network error")
  }
}

  const canSubmit =
    emailVerified &&
    // phoneVerified &&
    c1 &&
    c2 &&
    face &&
    audio

  return (
    <form
      onSubmit={submit}
      className="relative overflow-hidden w-full flex items-center flex-col gap-4 p-4"
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
      <div className="relative w-1/3 overflow-hidden">
        <motion.div
          animate={{ x: `-${step * 100}%` }}
          transition={{ duration: 0.3 }}
          className="flex w-full"
        >

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">Who are you?</p>
            <TextField name="First Name"/>
            <TextField name="Middle Name"/>
            <TextField name="Last Name"/>
            <TextField name="Suffix"/>
            <button type="button" onClick={next}>Next</button>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What is your email?</p>
            <VerifyEmail setter={setEmailVerified}/>
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What is your phone number?</p>
            <VerifyPhone setter={setPhoneVerified}/>
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="p-4 w-full shrink-0 flex flex-col gap-2">
            <p className="text-lg font-bold">What should we call you?</p>
            <TextField name="Username" />
            <label htmlFor="password">Password</label>
            <input type="password" id="password" name="password" />
            <label htmlFor="password">Confirm Password</label>
            <input type="password" id="password" name="password" />
            <label htmlFor="password">One More Time</label>
            <input type="password" id="password" name="password" />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="p-4 w-full shrink-0 flex flex-col gap-2">
            <p className="text-lg font-bold">Where are you?</p>
            <TextField name="Address Line 1" />
            <TextField name="Address Line 2" />
            <TextField name="City" />
            <TextField name="State" />
            <TextField name="Zip Code" />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">Where do you sleep?</p>
            <CoordinatePicker setter={setCoords}/>
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What do you look like?</p>
            <WebcamCapture setter={setFace}/>
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">What do you sound like?</p>
            <FiveSecondRecorder setter={setAudio}/>
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="p-4 w-full shrink-0 flex flex-col gap-2">
            <p className="text-lg font-bold">Do you have any money?</p>
            <TextField name="Credit Card Number" />
            <TextField name="Expiration Month" />
            <TextField name="Expiration Year" />
            <TextField name="CVC" />
            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>
              <button type="button" onClick={next}>Next</button>
            </div>
          </section>

          <section className="p-4 w-full shrink-0 flex flex-col gap-2">
            <p className="text-lg font-bold">A few more nuts and bolts</p>
            <TextField name="Social Security Number" />
            <TextField name="License Plate" />
            <TextField name="License Plate State" />
            <TextField name="Date of Birth" />
            <TextField name="Mother's Maiden Name" />
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

          <section className="w-full shrink-0 p-4 flex flex-col gap-2">
            <p className="text-lg font-bold">Are you sure?</p>

            <div>
              {!emailVerified && <p className="text-red-500 font-bold flex items-center"><X/> Unverified Email</p>}
              {/*{!phoneVerified && <p className="text-red-500 font-bold flex items-center"><X/> Unverified Phone Number</p>}*/}
              {!face && <p className="text-red-500 font-bold flex items-center"><X/> No Face Photo</p>}
              {!audio && <p className="text-red-500 font-bold flex items-center"><X/> No Voice Recording</p>}
              {!c1 && <p className="text-red-500 font-bold flex items-center"><X/> Incomplete CAPTCHA</p>}
              {!c2 && <p className="text-red-500 font-bold flex items-center"><X/> Incomplete CAPTCHA</p>}
            </div>

            <HCaptcha
              sitekey="370c332a-75f8-48c6-9562-d97e0a42f870"
              onVerify={(token) => setC2(token)}
            />

            <div className="flex justify-between">
              <button type="button" onClick={back}>Back</button>

              {canSubmit && (
                <input type="submit" className="px-4 py-2 !bg-green-600 text-white rounded"/>
              )}
            </div>
          </section>
        </motion.div>
      </div>
    </form>
  )
}

export default Page
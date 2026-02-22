'use client'

import TextField from "@/components/textField";
import HCaptcha from "@hcaptcha/react-hcaptcha";
import {useState} from "react";
import dynamic from "next/dynamic"
import WebcamCapture from "@/components/webcam-capture";
import VerifyEmail from "@/components/verify-email";
import VerifyPhone from "@/components/verify-phone";
import FiveSecondRecorder from "@/components/voice-record";
import {X} from "lucide-react";

const Page = () => {

  const [c1, setC1] = useState<string|null>(null)
  const [c2, setC2] = useState<string|null>(null)

  const [emailVerified, setEmailVerified] = useState(false)
  const [phoneVerified, setPhoneVerified] = useState(false)
  const [face, setFace] = useState<Blob|null>(null)
  const [audio, setAudio] = useState<Blob|null>(null)

  const submit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    // @ts-ignore
    formData.append('email', document.querySelector('[name="email"]').value);
    // @ts-ignore
    formData.append('phone', document.querySelector('[name="phone"]').value);

    // @ts-ignore
    formData.append("image", face, "photo.png")
    // @ts-ignore
    formData.append("voice", audio, "voice.webm")
    const data = Object.fromEntries(formData.entries())

    console.log(data)

    fetch("/api/validate_user",
      {
        method: 'POST',
        body: formData
      }).then((res) => res.json()).then((json) => console.log(json))
  }

  return (
    <div>
      <form onSubmit={submit} className="flex flex-col items-center justify-center gap-4 p-4">
        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">What is your email?</p>
          <VerifyEmail setter={setEmailVerified} />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">What is your phone number?</p>
          <VerifyPhone setter={setPhoneVerified} />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">What should we call you?</p>
          <TextField name="Username" />
          <label htmlFor="password">Password</label>
          <input type="password" id="password" name="password" />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">What do you look like?</p>
          <WebcamCapture setter={setFace} />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">What do you sound like?</p>
          <FiveSecondRecorder setter={setAudio} />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Are you a robot?</p>
          <HCaptcha
            sitekey="370c332a-75f8-48c6-9562-d97e0a42f870"
            onVerify={(token) => setC1(token)}
          />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Are you sure?</p>
          <HCaptcha
            sitekey="370c332a-75f8-48c6-9562-d97e0a42f870"
            onVerify={(token) => setC2(token)}
          />
        </section>

        {!emailVerified && <p className="text-red-500 font-bold flex items-center"><X/> Unverified Email</p>}
        {!phoneVerified && <p className="text-red-500 font-bold flex items-center"><X/> Unverified Phone Number</p>}
        {!face && <p className="text-red-500 font-bold flex items-center"><X/> No Face Photo</p>}
        {!audio && <p className="text-red-500 font-bold flex items-center"><X/> No Voice Recording</p>}
        {!c1 && <p className="text-red-500 font-bold flex items-center"><X/> Incomplete CAPTCHA</p>}
        {!c2 && <p className="text-red-500 font-bold flex items-center"><X/> Incomplete CAPTCHA</p>}
        {
          emailVerified &&
          phoneVerified &&
          c1 &&
          c2 &&
          face &&
          audio &&
          <input type="submit" className="w-1/3"/>
        }
        <input type="submit" className="w-1/3 !bg-pink-700"/>
      </form>
    </div>
  )
}

export default Page;
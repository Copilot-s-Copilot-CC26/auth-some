'use client'

import TextField from "@/components/textField";
import HCaptcha from "@hcaptcha/react-hcaptcha";
import {useEffect, useRef, useState} from "react";
import dynamic from "next/dynamic"
import WebcamCapture from "@/components/webcam-capture";
import VerifyEmail from "@/components/verify-email";

const CoordinatePicker = dynamic(
  () => import("@/components/coordinate-picker"),
  { ssr: false }
)

const Page = () => {

  const [token, setToken] = useState<string|null>(null);

  const submit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = Object.fromEntries(formData.entries())

    console.log(data)

    fetch("/api/create_user",
      {
        method: 'POST',
        headers: {
          'Content-Type': "application/json"
        },
        body: JSON.stringify(data)
      }).then((res) => res.json()).then((json) => console.log(json))
  }

  useEffect(() => {

    if (token)
      console.log(`hCaptcha Token: ${token}`);

  }, [token]);

  return (
    <div>
      <form onSubmit={submit} className="flex flex-col items-center justify-center gap-4 p-4">
        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Who are you?</p>
          <TextField name="First Name" />
          <TextField name="Middle Name"/>
          <TextField name="Last Name" />
          <TextField name="Suffix" />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">How can we reach you?</p>
          <VerifyEmail />
          <TextField name="Phone Number" />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">What should we call you?</p>
          <TextField name="Username" />
          <label htmlFor="password">Password</label>
          <input type="password" id="password" name="password" />
          <label htmlFor="password">Confirm Password</label>
          <input type="password" id="password" name="password" />
          <label htmlFor="password">One More Time</label>
          <input type="password" id="password" name="password" />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Where are you?</p>
          <TextField name="Address Line 1" />
          <TextField name="Address Line 2" />
          <TextField name="City" />
          <TextField name="State" />
          <TextField name="Zip Code" />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Where do you sleep?</p>
          <CoordinatePicker />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">What do you look like?</p>
          <WebcamCapture />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Does your drivers license also look like that?</p>
          <WebcamCapture />
        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Are you a robot?</p>
          <HCaptcha
            sitekey="370c332a-75f8-48c6-9562-d97e0a42f870"
            onVerify={(token) => setToken(token)}
          />

        </section>

        <section className="p-4 border-2 rounded-lg w-1/3 flex flex-col gap-1">
          <p className="text-lg font-bold">Are you sure?</p>
          <HCaptcha
            sitekey="370c332a-75f8-48c6-9562-d97e0a42f870"
            onVerify={(token) => setToken(token)}
          />
        </section>

        <input type="submit" className="w-1/3"/>
      </form>
    </div>
  )
}

export default Page;
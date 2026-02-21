'use client'

const Page = () => {

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

  return (
    <div>
      <form onSubmit={submit}>
        <label htmlFor="username">Username</label>
        <input id="username" name="username" />
        <label htmlFor="password">Password</label>
        <input id="password" name="password" />
        <input type="submit"/>
      </form>
    </div>
  )
}

export default Page;
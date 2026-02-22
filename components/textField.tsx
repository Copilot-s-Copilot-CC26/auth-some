

const TextField = ({ name }: { name: string }) => {

  return (
    <>
      <label
        htmlFor={name.replaceAll(" ", "-").toLowerCase()}
      >
        {name}
      </label>
      <input
        type="text"
        id={name.replaceAll(" ", "-").toLowerCase()}
        name={name.replaceAll(" ", "-").toLowerCase()}
      />
    </>
  )
}

export default TextField;
import { useState } from "react";
import Controller from "./components/Controller_localhost";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <>
        <Controller />
      </>
    </div>
  );
}

export default App;
import { useState } from "react";
import Login from "./Login";
import Chat from "./Chat";
import "./App.css";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
//  const [loggedIn, setLoggedIn] = useState(
//    !!localStorage.getItem("session_id")
//  );

  return loggedIn ? (
    <Chat logout={() => setLoggedIn(false)} />
  ) : (
    <Login onLogin={() => setLoggedIn(true)} />
  );
}

export default App;



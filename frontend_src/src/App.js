import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import MainTrafficPage from "./pages/MainTrafficPage";
import './App.css';
import InDoorPage from "./pages/InDoorPage";

function App() {

  return (
    <div className="App">
      <Router>
        <Switch>
          <Route exact path="/traffic">
            <MainTrafficPage />
          </Route>
          <Route path="/">
            <InDoorPage />
          </Route>
        </Switch>
      </Router>
    </div>
  );
}

export default App;

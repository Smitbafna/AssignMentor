import React, { Component } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import Room from "./Room";
import SignIn from "./sign-in/SignIn.js"
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";

export default class HomePage extends Component {
  render() {
    return (
      <Router>
        <div>
          {/* Navigation Links */}
          <nav>
            <Link to="/">Home</Link> |{" "}
            <Link to="/join">Join Room</Link> |{" "}
            <Link to="/create">Create Room</Link>
          </nav>

          <Routes>
            <Route path="/" element={<p>This is the home page</p>} />
            <Route path="/join" element={<RoomJoinPage />} />
            <Route path="/create" element={<CreateRoomPage />} />
            <Route path="/room/:roomCode" element={<Room />} />
            {/* Redirect to home page if route does not match */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </Router>
    );
  }
}

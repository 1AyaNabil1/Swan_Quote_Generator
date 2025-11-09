import React from "react";
import AnimatedBackground from "./components/AnimatedBackground";
import QuoteGenerator from "./components/QuoteGenerator";
import "./App.css";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <div className="relative h-screen bg-black overflow-hidden">
      {/* Animated Background with Purple Dots */}
      <AnimatedBackground />

      {/* Main Content */}
      <main className="relative z-10 h-full">
        <QuoteGenerator />
        <Toaster
  position="top-right"
  reverseOrder={false}
/>
{" "}
      </main>
    </div>
  );
}

export default App;

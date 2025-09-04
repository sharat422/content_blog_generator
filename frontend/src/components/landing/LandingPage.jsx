import React from "react";
import Hero from "./Hero";
import Features from "./Features";
import Testimonials from "./Testimonials";
import Navbar from "../ui/Navbar";

export default function LandingPage({ onGenerate }) {
  return (
    <>
      <Navbar />
      <Hero onGenerate={onGenerate} />
      <Features />
      <Testimonials />
      {/* Optionally add a call-to-action footer */}
    </>
  );
}

// src/context/AuthContext.jsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);


  // ------------------------------
  // Load session on app start
  // ------------------------------
  useEffect(() => {
    const loadUser = async () => {
      try {
        const { data, error } = await supabase.auth.getUser();

        if (error) {
          console.warn("No session:", error.message);
          setUser(null);
        } else {
          setUser(data?.user ?? null);
        }
      } catch (err) {
        console.error("Error:", err.message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUser();

    // Listen for login/logout
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
      setLoading(false);
    });

    return () => sub.subscription.unsubscribe();
  }, []);

  // ------------------------------
  // Sign Up
  // ------------------------------
  const signUp = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (error) throw error;

    // ⚠️ Only create twin_profiles entry if user exists
    if (data?.user) {
      const { error: twinError } = await supabase
        .from("twin_profiles")
        .insert([
          {
            user_id: data.user.id,
            display_name: email.split("@")[0],
            favorite_topics: [],
          },
        ]);

      // Ignore conflict errors (duplicate)
      if (twinError && twinError.code !== "23505") {
        console.error("Error creating twin profile:", twinError.message);
      }
    }

    return data;
  };

  // ------------------------------
  // Login
  // ------------------------------
  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    return data;
  };



  // ------------------------------
  // Logout
  // ------------------------------
  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    setUser(null); // important
  };

  const getToken = async () => {
    const { data } = await supabase.auth.getSession();
    return data?.session?.access_token || null;
  };

  return (
    <AuthContext.Provider value={{ user, loading, signUp, signIn, signOut, getToken }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook
export function useAuth() {
  return useContext(AuthContext);
}

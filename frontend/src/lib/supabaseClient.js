import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://ndqksyjrmhfgxeyrygog.supabase.co";
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kcWtzeWpybWhmZ3hleXJ5Z29nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3MzgwMjgsImV4cCI6MjA3MjMxNDAyOH0.6DfEhrvPxwd8gLrxs8MWCAwbZiixS1snIZ4nfJ6zjyQ";

// Debug log (remove after testing!)
console.log("VITE_SUPABASE_URL:", supabaseUrl);
console.log("VITE_SUPABASE_ANON_KEY:", supabaseAnonKey ? "✅ loaded" : "❌ missing");

export const supabase = createClient(supabaseUrl, supabaseAnonKey);


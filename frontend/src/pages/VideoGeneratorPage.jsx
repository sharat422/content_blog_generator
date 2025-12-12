// src/pages/VideoGeneratorPage.jsx

import React, { useState } from "react";
import { Loader2, Video, ImageIcon } from "lucide-react";
import { useAuth } from "../context/AuthContext";
//import VideoPlayer from "../components/video_renderer"; // Assuming you have a VideoPlayer component
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";

//import { Textarea } from "../components/ui/textarea";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// NOTE: Hardcoding costs. Ideally, these would come from a context/config.
const COST_PLAN_BASIC = 8;
const COST_IMAGE_GEN_BASIC = 25;
const COST_VIDEO_RENDER_BASIC = 100;

export default function VideoGeneratorPage() {
  const { user, setCredits } = useAuth();
  const authToken = user?.token;

  // Shared States
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("engaging");
  // Modes: "shorts" | "youtube" | "image"
  const [mode, setMode] = useState("shorts");
  const [error, setError] = useState("");

  // Shorts / Reels Generator States
  const [scenes, setScenes] = useState([]);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [loadingRender, setLoadingRender] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [withVoiceover, setWithVoiceover] = useState(true);

  // Dedicated Image Generator States
  const [imagePrompt, setImagePrompt] = useState(
    "A stunning, vertical 9:16 portrait of a futuristic city skyline at sunset, cyberpunk aesthetic, high detail.",
  );
  const [imageUrl, setImageUrl] = useState("");
  const [loadingImage, setLoadingImage] = useState(false);

  // YouTube Generator States
  const [ytScript, setYtScript] = useState("");
  const [ytVideoUrl, setYtVideoUrl] = useState("");
  const [ytLoadingScript, setYtLoadingScript] = useState(false);
  const [ytLoadingVideo, setYtLoadingVideo] = useState(false);
  const [withMusic, setWithMusic] = useState(true);

  const hasScenes = scenes && scenes.length > 0;

  // Utility to update a specific scene
  const updateScene = (index, field, value) => {
    setScenes((prevScenes) => {
      const newScenes = [...prevScenes];
      newScenes[index] = { ...newScenes[index], [field]: value };
      return newScenes;
    });
  };

  // -------------------------------------------------------------------
  // 1. DEDICATED IMAGE GENERATION
  // -------------------------------------------------------------------

  async function handleGenerateImage() {
    setError("");
    setImageUrl("");
    if (!imagePrompt.trim()) {
      return setError("Please enter a detailed image prompt.");
    }
    setLoadingImage(true);

    try {
      const res = await fetch(`${API_BASE}/api/image/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({ prompt: imagePrompt }),
      });

      if (res.status === 402) {
        throw new Error(
          `Credit Error: Not enough credits. Image generation costs ${COST_IMAGE_GEN_BASIC}.`,
        );
      }
      if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
      }

      const data = await res.json();
      setImageUrl(data.image_url);
      // NOTE: This assumes the image generation endpoint returns the final credit amount or
      // you have a separate API call to fetch the updated credits.
      if (setCredits) setCredits((prev) => prev - COST_IMAGE_GEN_BASIC); 
    } catch (err) {
      console.error(err);
      setError(err.message || "Image generation failed.");
    } finally {
      setLoadingImage(false);
    }
  }

  // -------------------------------------------------------------------
  // 2. SHORTS/REELS GENERATOR
  // -------------------------------------------------------------------

  // Step 1: Generate Plan
  async function handlePlan() {
    setError("");
    setVideoUrl("");
    setScenes([]);
    if (!topic.trim()) {
      return setError("Please enter a video topic.");
    }
    setLoadingPlan(true);

    try {
      const res = await fetch(`${API_BASE}/api/video/plan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({ topic, style }),
      });

      if (res.status === 402) {
        throw new Error(
          `Credit Error: Not enough credits. Planning costs ${COST_PLAN_BASIC}.`,
        );
      }
      if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
      }

      const data = await res.json();
      setScenes(data.scenes);
      // The plan step deducts the planning credit
      if (setCredits) setCredits((prev) => prev - COST_PLAN_BASIC); 
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to generate video plan.");
    } finally {
      setLoadingPlan(false);
    }
  }

  // Step 2: Render Video
  async function handleRender() {
    setError("");
    setVideoUrl("");
    if (!hasScenes) {
      return setError("Please generate a scene plan first.");
    }
    setLoadingRender(true);

    try {
      const res = await fetch(`${API_BASE}/api/video/render`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        // The scenes array includes the image_prompt field
        body: JSON.stringify({ scenes, with_voiceover: withVoiceover }),
      });

      if (res.status === 402) {
        throw new Error(
          `Credit Error: Not enough credits. Video render costs ~${COST_VIDEO_RENDER_BASIC} plus image/voiceover costs.`,
        );
      }
      if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
      }

      const data = await res.json();
      setVideoUrl(data.video_url);

      // NOTE: The render endpoint deducts ALL remaining credits (render + image + voiceover).
      // You must implement a logic here to refresh/deduct the correct amount.
      // For now, we will simply trigger a refresh or deduct a large placeholder amount.
      if (setCredits) setCredits((prev) => prev - 150); // Placeholder deduction
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to render video.");
    } finally {
      setLoadingRender(false);
    }
  }

  // -------------------------------------------------------------------
  // 3. YOUTUBE GENERATOR (Placeholder remains the same)
  // -------------------------------------------------------------------

  // Placeholder function for YouTube flow
  async function handleGenerateYtScript() {
    setError("YouTube flow is a placeholder in this update.");
  }
  
  // Placeholder function for YouTube rendering
  async function handleRenderYtVideo() {
    setError("YouTube flow is a placeholder in this update.");
  }


  // -------------------------------------------------------------------
  // JSX RENDER
  // -------------------------------------------------------------------

  const sharedControls = (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold">Video Style</h2>
      <div className="flex gap-4">
        <Button
          variant={style === "engaging" ? "default" : "outline"}
          onClick={() => setStyle("engaging")}
        >
          Engaging / Viral
        </Button>
        <Button
          variant={style === "informative" ? "default" : "outline"}
          onClick={() => setStyle("informative")}
        >
          Informative / Educational
        </Button>
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto py-12 px-4">
      <h1 className="text-4xl font-bold mb-8 text-center">
        AI Content & Video Generator 🎬
      </h1>

      {/* MODE TOGGLE */}
      <div className="flex justify-center gap-2 mb-8">
        <Button
          variant={mode === "shorts" ? "default" : "outline"}
          onClick={() => setMode("shorts")}
          className="flex items-center gap-2"
        >
          <Video size={16} /> Vertical Shorts / Reels
        </Button>
        <Button
          variant={mode === "image" ? "default" : "outline"}
          onClick={() => setMode("image")}
          className="flex items-center gap-2"
        >
          <ImageIcon size={16} /> Dedicated AI Image
        </Button>
        <Button
          variant={mode === "youtube" ? "default" : "outline"}
          onClick={() => setMode("youtube")}
          className="flex items-center gap-2"
          disabled // Keep YouTube as a placeholder for simplicity
        >
          YouTube Long-Form (WIP)
        </Button>
      </div>

      {/* ERROR DISPLAY */}
      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-300 p-3 rounded-md mb-6">
          {error}
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* MODE: DEDICATED AI IMAGE GENERATION */}
      {/* ------------------------------------------------------------------- */}
      {mode === "image" && (
        <Card className="max-w-4xl mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon /> Generate Single AI Image (DALL-E)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <Textarea
              value={imagePrompt}
              onChange={(e) => setImagePrompt(e.target.value)}
              placeholder="Enter a detailed, creative prompt for your vertical (9:16) image."
              className="min-h-[150px]"
            />

            <Button
              onClick={handleGenerateImage}
              disabled={loadingImage || !authToken}
              className="w-full"
            >
              {loadingImage ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                `Generate Image (Costs ${COST_IMAGE_GEN_BASIC} Credits)`
              )}
            </Button>

            {imageUrl && (
              <div className="pt-4 border-t border-gray-700">
                <h3 className="text-lg font-semibold mb-3">Generated Image</h3>
                <div className="flex justify-center">
                  {/* Aspect ratio set to 9:16 for a vertical display */}
                  <img
                    src={imageUrl}
                    alt="AI Generated"
                    className="w-full max-w-xs rounded-xl shadow-lg border border-gray-700"
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* MODE: SHORTS/REELS GENERATOR */}
      {/* ------------------------------------------------------------------- */}
      {mode === "shorts" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* CONTROL PANEL (LEFT 1/3) */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>1. Define Video</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex flex-col gap-2">
                <h2 className="text-xl font-semibold">Video Topic</h2>
                <Input
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., 'Three ways to make money with AI'"
                />
              </div>

              {sharedControls}

              <Button
                onClick={handlePlan}
                disabled={loadingPlan || loadingRender || !authToken}
                className="w-full"
              >
                {loadingPlan ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  `Generate Scene Plan (Costs ${COST_PLAN_BASIC} Credits)`
                )}
              </Button>
            </CardContent>
          </Card>

          {/* SCENES & RENDER (RIGHT 2/3) */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>2. Edit Scenes & Render</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* SCENE EDITOR */}
              {hasScenes && (
                <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
                  <p className="text-sm text-gray-400">
                    Edit the caption, duration, and **AI Image Prompt** for each
                    scene before rendering.
                  </p>
                  {scenes.map((scene, idx) => (
                    <div
                      key={scene.id}
                      className="p-4 border border-gray-700 rounded-xl space-y-2"
                    >
                      <h4 className="font-semibold text-lg text-primary">
                        Scene {idx + 1}
                      </h4>

                      <label className="block text-sm font-medium">
                        On-Screen Caption
                      </label>
                      <Input
                        type="text"
                        value={scene.caption}
                        onChange={(e) =>
                          updateScene(idx, "caption", e.target.value)
                        }
                        placeholder="Short text for the screen"
                      />

                      <label className="block text-sm font-medium pt-2">
                        AI Image Prompt
                      </label>
                      <Textarea
                        value={scene.image_prompt || ""}
                        onChange={(e) =>
                          updateScene(idx, "image_prompt", e.target.value)
                        }
                        className="min-h-[60px]"
                        placeholder="Detailed prompt for background image (vertical 9:16)"
                      />

                      <label className="block text-sm font-medium pt-2">
                        Duration (seconds)
                      </label>
                      <Input
                        type="number"
                        min="3"
                        max="10"
                        value={scene.duration_sec}
                        onChange={(e) =>
                          updateScene(
                            idx,
                            "duration_sec",
                            parseInt(e.target.value) || 5,
                          )
                        }
                        className="w-20"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* RENDER CONTROLS */}
              {hasScenes && (
                <div className="pt-4 border-t border-gray-700 space-y-4">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      id="voiceover"
                      checked={withVoiceover}
                      onChange={() => setWithVoiceover(!withVoiceover)}
                      className="h-4 w-4 text-green-600 border-gray-600 rounded"
                    />
                    <label htmlFor="voiceover" className="text-sm font-medium">
                      Include AI Voiceover (Text-to-Speech)
                    </label>
                  </div>

                  <Button
                    onClick={handleRender}
                    disabled={loadingRender || !authToken}
                    className="w-full"
                  >
                    {loadingRender ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      `Render Final Video (AI Images + Voiceover)`
                    )}
                  </Button>
                </div>
              )}

              {/* VIDEO PREVIEW */}
              {videoUrl && (
                <div className="pt-4 border-t border-gray-700">
                  <h3 className="text-lg font-semibold mb-3">
                    Final Video Preview
                  </h3>
                  <div className="flex justify-center">
                    <VideoPlayer src={videoUrl} />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* MODE: YOUTUBE GENERATOR (Placeholder) */}
      {/* ------------------------------------------------------------------- */}
      {mode === "youtube" && (
        <Card className="max-w-4xl mx-auto">
          <CardHeader>
            <CardTitle>YouTube Long-Form Video Generator (Placeholder)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col gap-2">
              <h2 className="text-xl font-semibold">Video Topic</h2>
              <Input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., 'The complete history of renewable energy'"
              />
            </div>
            {sharedControls}
            <Button
              onClick={handleGenerateYtScript}
              disabled={ytLoadingScript || !authToken}
              className="w-full"
            >
              Generate Long-Form Script (WIP)
            </Button>

            {ytScript && (
              <div className="space-y-4">
                <Textarea
                  value={ytScript}
                  onChange={(e) => setYtScript(e.target.value)}
                  className="min-h-[300px]"
                />
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="music"
                    checked={withMusic}
                    onChange={() => setWithMusic(!withMusic)}
                    className="h-4 w-4 text-green-600 border-gray-600 rounded"
                  />
                  <label htmlFor="music" className="text-sm font-medium">
                    Add Background Music
                  </label>
                </div>
                <Button
                  onClick={handleRenderYtVideo}
                  disabled={ytLoadingVideo || !authToken}
                  className="w-full"
                >
                  Render YouTube Video (WIP)
                </Button>
              </div>
            )}
            {ytVideoUrl && (
              <div className="pt-4 border-t border-gray-700">
                <h3 className="text-lg font-semibold mb-3">
                  Final Video Preview
                </h3>
                <div className="flex justify-center">
                  <VideoPlayer src={ytVideoUrl} />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
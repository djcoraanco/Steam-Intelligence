"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { cn } from "@/lib/utils";
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Info,
  Image as ImageIcon,
  FileText,
  Tag,
  Globe2,
  ListChecks,
  Copy,
  Check,
  Gamepad2
} from "lucide-react";

interface CapsuleSpec {
  name: string;
  width: number;
  height: number;
  required: boolean;
  notes: string;
}

const CAPSULE_SPECS: CapsuleSpec[] = [
  { name: "Header Capsule", width: 460, height: 215, required: true, notes: "Main store browse image & library header" },
  { name: "Main / Large Capsule", width: 616, height: 353, required: true, notes: "Featured & Recommended carousel and Daily Deals" },
  { name: "Small Capsule", width: 231, height: 87, required: true, notes: "Wishlist emails, recommendations, search popup results" },
  { name: "Vertical Hero Capsule", width: 374, height: 448, required: true, notes: "Steam Library grid view (2:3 aspect ratio)" },
  { name: "Page Background", width: 1438, height: 810, required: false, notes: "Ambient background art on desktop store page" }
];

const RECOMMENDED_LANGUAGES = [
  { code: "en", name: "English (US/UK)", weight: "Mandatory (Primary store language)" },
  { code: "zh-CN", name: "Simplified Chinese", weight: "Critical (~25-30% Steam users)" },
  { code: "de", name: "German", weight: "High (Top European PC market)" },
  { code: "fr", name: "French", weight: "High (EFIGS core)" },
  { code: "es", name: "Spanish (Spain & LatAm)", weight: "High (EFIGS core)" },
  { code: "ja", name: "Japanese", weight: "Medium-High (Growing PC market)" },
  { code: "ko", name: "Korean", weight: "Medium (Dedicated PC player base)" },
  { code: "pt-BR", name: "Brazilian Portuguese", weight: "Medium-High (High engagement)" },
  { code: "ru", name: "Russian", weight: "Medium (Large volume market)" }
];

export default function StoreOptimizerPage() {
  const [shortDesc, setShortDesc] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([
    "Deckbuilding",
    "Roguelike",
    "Turn-Based Strategy",
    "Card Battler",
    "Singleplayer"
  ]);
  const [newTagInput, setNewTagInput] = useState("");
  const [copied, setCopied] = useState(false);

  // Short description metrics
  const charCount = shortDesc.length;
  const wordCount = shortDesc.trim() ? shortDesc.trim().split(/\s+/).length : 0;
  const isOptimalLength = charCount >= 120 && charCount <= 280;

  const handleAddTag = () => {
    if (newTagInput.trim() && !selectedTags.includes(newTagInput.trim())) {
      setSelectedTags([...selectedTags, newTagInput.trim()]);
      setNewTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setSelectedTags(selectedTags.filter((t) => t !== tagToRemove));
  };

  const handleCopyTags = () => {
    navigator.clipboard.writeText(selectedTags.join(", "));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold tracking-tight text-white">Store Page Optimizer</h1>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Steamworks conversion optimization tools: capsule dimension validation, description hook testing, tag weighting, and localization coverage.
            </p>
          </div>
        </div>

        {/* Top Section: Short Description Analyzer */}
        <div className="bg-card border border-border rounded-lg p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              <h2 className="text-base font-semibold text-white">Short Description Hook Analyzer</h2>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className={cn(charCount > 300 ? "text-rose-400 font-bold" : "text-muted-foreground")}>
                Characters: <span className="text-white font-medium">{charCount}</span> / 300 max
              </span>
              <span className="text-muted-foreground">
                Words: <span className="text-white font-medium">{wordCount}</span> (ideal: 40-55)
              </span>
            </div>
          </div>

          <textarea
            rows={4}
            value={shortDesc}
            onChange={(e) => setShortDesc(e.target.value)}
            placeholder="Paste your Steam store short description here to analyze character count, hook clarity, and fold visibility..."
            className="w-full p-3 bg-background border border-border rounded-md text-sm text-white placeholder-muted-foreground focus:outline-none focus:border-primary resize-y"
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div
              className={cn(
                "p-3 rounded border flex items-start gap-2",
                charCount === 0
                  ? "bg-card border-border text-muted-foreground"
                  : isOptimalLength
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : charCount > 300
                  ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                  : "bg-yellow-500/10 border-yellow-500/30 text-yellow-300"
              )}
            >
              {charCount > 300 ? (
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              ) : isOptimalLength ? (
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
              ) : (
                <Info className="w-4 h-4 shrink-0 text-yellow-400" />
              )}
              <div>
                <div className="font-semibold">Above-the-Fold Cutoff</div>
                <div className="text-[11px] mt-0.5">
                  {charCount > 300
                    ? "Exceeds 300 chars: text will be cut off with 'Read more' or overflow below fold."
                    : isOptimalLength
                    ? "Optimal length: fits completely above the fold on all standard 1080p monitors."
                    : "Slightly short or empty. Aim for 140-260 characters explaining genre + core mechanic."}
                </div>
              </div>
            </div>

            <div className="p-3 rounded border border-border bg-card text-muted-foreground">
              <div className="font-semibold text-white">Rule 1: Name the Genre First</div>
              <div className="text-[11px] mt-0.5">
                Always state what the player actually does within the first 12 words (e.g., &quot;A roguelike deckbuilder where you...&quot;).
              </div>
            </div>

            <div className="p-3 rounded border border-border bg-card text-muted-foreground">
              <div className="font-semibold text-white">Rule 2: Avoid Lore Fluff</div>
              <div className="text-[11px] mt-0.5">
                Avoid introductory lore (&quot;In a realm torn by darkness...&quot;). Steam shoppers bounce in under 3 seconds without gameplay hooks.
              </div>
            </div>
          </div>
        </div>

        {/* Section: Tag Order & Recommendation Weighting */}
        <div className="bg-card border border-border rounded-lg p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <Tag className="w-5 h-5 text-chart-2" />
                <h2 className="text-base font-semibold text-white">Steam Tag Hierarchy & Algorithm Weights</h2>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                Steam&apos;s recommendation algorithm weighs your top 5 tags for 80% of &quot;More Like This&quot; matching.
              </p>
            </div>
            <button
              onClick={handleCopyTags}
              className="px-3 py-1.5 bg-background border border-border hover:border-gray-500 rounded text-xs text-white flex items-center gap-1.5 transition-colors self-start sm:self-auto"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? "Copied" : "Copy Tags"}
            </button>
          </div>

          <div className="flex flex-wrap gap-2 items-center">
            {selectedTags.map((tag, idx) => (
              <div
                key={tag}
                className={cn(
                  "px-3 py-1.5 rounded-md text-xs font-medium flex items-center gap-2 border",
                  idx < 5
                    ? "bg-primary/15 text-primary border-primary/40 font-semibold"
                    : "bg-background text-gray-300 border-border"
                )}
              >
                <span className="text-[10px] opacity-75">#{idx + 1}</span>
                <span>{tag}</span>
                {idx < 5 && <span className="text-[9px] bg-primary/20 px-1 rounded uppercase">Core 80%</span>}
                <button
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-rose-400 ml-1 text-gray-500"
                >
                  &times;
                </button>
              </div>
            ))}

            <div className="flex items-center gap-1">
              <input
                type="text"
                placeholder="Add tag..."
                value={newTagInput}
                onChange={(e) => setNewTagInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddTag()}
                className="px-2.5 py-1 bg-background border border-border rounded text-xs text-white placeholder-muted-foreground focus:outline-none focus:border-primary w-28"
              />
              <button
                onClick={handleAddTag}
                className="px-2 py-1 bg-primary text-black font-semibold rounded text-xs hover:bg-primary/90"
              >
                Add
              </button>
            </div>
          </div>
        </div>

        {/* Section: Capsule Asset Specifications Table */}
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ImageIcon className="w-5 h-5 text-chart-4" />
              <h2 className="text-sm font-semibold text-white">Steamworks Capsule Dimension Matrix</h2>
            </div>
            <span className="text-xs text-muted-foreground">Steamworks requirements checklist</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0e1422] text-muted-foreground border-b border-border">
                <tr>
                  <th className="py-3 px-4">Asset Type</th>
                  <th className="py-3 px-3">Dimensions (W x H)</th>
                  <th className="py-3 px-3">Aspect Ratio</th>
                  <th className="py-3 px-3">Requirement</th>
                  <th className="py-3 px-4">Store Placement & Purpose</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {CAPSULE_SPECS.map((spec) => (
                  <tr key={spec.name} className="hover:bg-accent/40 transition-colors">
                    <td className="py-3 px-4 font-semibold text-white">{spec.name}</td>
                    <td className="py-3 px-3 font-mono text-primary font-semibold">
                      {spec.width} &times; {spec.height} px
                    </td>
                    <td className="py-3 px-3 text-muted-foreground">
                      {(spec.width / spec.height).toFixed(2)}:1
                    </td>
                    <td className="py-3 px-3">
                      {spec.required ? (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/30 font-medium">
                          Mandatory
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-muted text-muted-foreground">
                          Optional
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-300">{spec.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section: Localization Matrix */}
        <div className="bg-card border border-border rounded-lg p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Globe2 className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-semibold text-white">Localization & Territory Priority Matrix</h2>
          </div>
          <p className="text-xs text-muted-foreground">
            Translating the store page text into these 9 languages unlocks over 92% of the global Steam PC active buyer base.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-2">
            {RECOMMENDED_LANGUAGES.map((lang) => (
              <div key={lang.code} className="p-3 bg-background border border-border rounded-lg flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-white">{lang.name}</div>
                  <div className="text-[11px] text-muted-foreground">{lang.weight}</div>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.5 bg-muted rounded text-primary">
                  {lang.code}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

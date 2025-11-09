import { useState } from "react";
import toast, { Toaster } from "react-hot-toast";

const toastStyles = {
  success: {
    className:
      "bg-green-800 text-white rounded-lg shadow-lg px-4 py-2 flex items-center gap-2 animate-slide-in",
    duration: 3000,
    icon: "✨",
  },
  error: {
    className:
      "bg-red-800 text-white rounded-lg shadow-lg px-4 py-2 flex items-center gap-2 animate-slide-in",
    duration: 4000,
    icon: "❌",
  },
  warning: {
    className:
      "bg-yellow-700 text-white rounded-lg shadow-lg px-4 py-2 flex items-center gap-2 animate-slide-in",
    duration: 3000,
    icon: "⚠️",
  },
  info: {
    className:
      "bg-blue-800 text-white rounded-lg shadow-lg px-4 py-2 flex items-center gap-2 animate-slide-in",
    duration: 2000,
    icon: "ℹ️",
  },
  loading: {
    className:
      "bg-gray-800 text-white rounded-lg shadow-lg px-4 py-2 flex items-center gap-2 animate-slide-in",
    icon: "🤔",
  },
};

const QuoteGenerator = () => {
  const [quote, setQuote] = useState("");
  const [author, setAuthor] = useState("");
  const [category, setCategory] = useState("motivation");
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("");
  const [loading, setLoading] = useState(false);

  const categories = [
    "motivation",
    "inspiration",
    "wisdom",
    "humor",
    "love",
    "success",
    "life",
    "friendship",
    "happiness",
    "random",
  ];

  const handleGenerateQuote = async () => {
    if (!category) {
      toast("Please select a category", toastStyles.warning);
      return;
    }

    const requestCount = parseInt(localStorage.getItem("requestCount") || "0");
    if (requestCount > 50) {
      toast("Rate limit approaching. Please slow down.", toastStyles.warning);
      return;
    }

    setLoading(true);
    const toastId = toast.loading(
      "Generating your quote...",
      toastStyles.loading
    );

    try {
      const response = await fetch("/api/quotes/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category, topic, style }),
      });

      if (!response.ok) throw new Error("Failed to generate quote");

      const data = await response.json();
      setQuote(data.quote);
      setAuthor(data.author || "Swan");

      localStorage.setItem("requestCount", (requestCount + 1).toString());

      toast.success("Quote generated successfully!", {
        id: toastId,
        ...toastStyles.success,
      });
    } catch (error) {
      console.error(error);
      toast.error("Failed to generate quote. Please try again.", {
        id: toastId,
        ...toastStyles.error,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyQuote = () => {
    if (!quote) {
      toast("Generate a quote first!", toastStyles.info);
      return;
    }

    navigator.clipboard
      .writeText(`"${quote}" - ${author}`)
      .then(() => {
        toast.success("Quote copied to clipboard!", toastStyles.success);
      })
      .catch(() => {
        toast.error("Failed to copy quote", toastStyles.error);
      });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Toaster */}
      <Toaster position="top-right" />

      {/* Hero */}
      <div className="flex-shrink-0 text-center px-4 md:px-8 pb-4 md:pb-8 pt-2">
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-normal text-white tracking-tight font-serif">
          Swan
        </h1>
        <p className="text-white/60 text-sm md:text-base lg:text-lg max-w-xl mx-auto font-light tracking-wide px-4">
          Because sometimes, the right words can light the stars inside you
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 px-4 md:px-8 pb-4 md:pb-8 overflow-y-auto md:overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-8 h-full">
          {/* Quote Display */}
          <div className="flex items-center justify-center order-2 lg:order-1">
            <div className="w-full max-w-2xl border border-purple-primary/20 rounded-xl md:rounded-2xl p-4 md:p-8 lg:p-12 min-h-[180px] md:min-h-[280px] flex items-center justify-center bg-gradient-to-br from-purple-primary/20 via-purple-accent/10 to-transparent backdrop-blur-sm">
              {quote ? (
                <div className="space-y-3 md:space-y-6 w-full">
                  <div className="text-lg md:text-2xl lg:text-3xl font-serif text-white/90 leading-relaxed italic">
                    "{quote}"
                  </div>
                  {author && (
                    <div className="text-right text-sm md:text-base text-purple-light/80 font-light">
                      — {author}
                    </div>
                  )}
                  <button
                    onClick={handleCopyQuote}
                    className="mt-3 md:mt-6 px-4 md:px-5 py-2 bg-purple-primary/20 hover:bg-purple-primary/30 border border-purple-primary/40 rounded-lg text-white text-xs md:text-sm font-light transition-all w-full md:w-auto"
                  >
                    Copy Quote
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <p className="text-base md:text-xl text-white/30 italic font-light">
                    Your quote will appear here...
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-start md:items-center justify-center order-1 lg:order-2">
            <div className="w-full max-w-md space-y-3 md:space-y-5">
              <div>
                <label className="block text-white/70 font-light mb-2 text-sm">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-4 py-2 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm focus:outline-none focus:border-purple-accent transition-all cursor-pointer"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-white/70 font-light mb-2 text-sm">
                  Topic (optional)
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., perseverance, courage..."
                  className="w-full px-4 py-2 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-purple-accent transition-all"
                />
              </div>

              <div>
                <label className="block text-white/70 font-light mb-2 text-sm">
                  Style (optional)
                </label>
                <input
                  type="text"
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  placeholder="e.g., Shakespeare, modern..."
                  className="w-full px-4 py-2 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-purple-accent transition-all"
                />
              </div>

              <button
                onClick={handleGenerateQuote}
                disabled={loading}
                className="w-full px-6 py-3 bg-gradient-to-r from-purple-primary via-purple-accent to-purple-primary hover:from-purple-accent hover:via-purple-light hover:to-purple-accent rounded-full text-white text-sm font-medium shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Generating..." : "Generate Quote"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center pb-4 md:pb-6 flex-shrink-0">
        <p className="text-white/60 text-xs md:text-sm font-light">
          Built by{" "}
          <a
            href="https://ayanexus.dev/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-purple-light hover:text-purple-accent font-medium"
          >
            AyaNexus
          </a>{" "}
          🦢
        </p>
      </footer>
    </div>
  );
};

export default QuoteGenerator;

import React, { useState } from 'react';

const QuoteGenerator = () => {
  const [quote, setQuote] = useState('');
  const [author, setAuthor] = useState('');
  const [category, setCategory] = useState('motivation');
  const [topic, setTopic] = useState('');
  const [style, setStyle] = useState('');
  const [loading, setLoading] = useState(false);

  const categories = [
    'motivation', 'inspiration', 'wisdom', 'humor', 
    'love', 'success', 'life', 'friendship', 'happiness', 'random'
  ];

  const handleGenerateQuote = async () => {
    setLoading(true);
    try {
      const requestBody = {
        category: category || 'random',
        topic: topic || null,
        style: style || null,
        length: 'medium'
      };

      const response = await fetch('http://localhost:8000/api/quotes/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate quote');
      }

      const data = await response.json();
      setQuote(data.quote);
      setAuthor(data.author || 'Ayō');
    } catch (error) {
      console.error('Error generating quote:', error);
      setQuote('Failed to generate quote. Please make sure the backend server is running.');
      setAuthor('');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyQuote = () => {
    if (quote) {
      navigator.clipboard.writeText(`"${quote}" - ${author}`);
      alert('Quote copied to clipboard!');
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-6">
        <div className="flex items-center space-x-3">
          {/* Empty left side for balance */}
        </div>
        <a 
          href="https://github.com/1AyaNabil1/Ai-Quotes-Generator"
          target="_blank"
          rel="noopener noreferrer"
          className="text-white/60 hover:text-white transition-colors"
          aria-label="View on GitHub"
        >
          <svg
            className="w-6 h-6"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
          </svg>
        </a>
      </header>

      {/* Hero Section - Center */}
      <div className="flex-shrink-0 text-center px-8 pb-12 pt-2">
        <div className="flex flex-col items-center space-y-3">
          <h1 className="text-7xl md:text-8xl font-normal text-white tracking-tight" style={{ fontFamily: "'Courier New', 'Courier', monospace", fontWeight: 400 }}>
            Ayō
          </h1>
          <p className="text-white/60 text-base md:text-lg max-w-xl font-light tracking-wide" style={{ fontFamily: "'Courier New', 'Courier', monospace" }}>
            AI quote generator to tailor your mood and preferences
          </p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 px-8 pb-8 overflow-hidden">
        {/* Left Column - Quote Display */}
        <div className="flex items-center justify-center">
          <div className="w-full max-w-2xl border border-purple-primary/20 rounded-2xl p-8 md:p-12 min-h-[280px] flex items-center justify-center bg-gradient-to-br from-purple-primary/20 via-purple-accent/10 to-transparent backdrop-blur-sm">
            {quote ? (
              <div className="space-y-6 w-full">
                <div className="text-2xl md:text-3xl font-serif text-white/90 leading-relaxed italic" style={{ fontFamily: "'Crimson Text', 'Georgia', serif" }}>
                  "{quote}"
                </div>
                {author && (
                  <div className="text-right text-base text-purple-light/80 font-light">
                    — {author}
                  </div>
                )}
                <button 
                  onClick={handleCopyQuote}
                  className="mt-6 px-5 py-2 bg-purple-primary/20 hover:bg-purple-primary/30 border border-purple-primary/40 rounded-lg text-white text-sm font-light transition-all" style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
                >
                  Copy Quote
                </button>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-xl text-white/30 italic font-light" style={{ fontFamily: "'Crimson Text', 'Georgia', serif" }}>
                  Your quote will appear here...
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Controls */}
        <div className="flex items-center justify-center">
          <div className="w-full max-w-md space-y-5" style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}>
            <div>
              <label className="block text-white/70 font-light mb-2 text-sm">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2.5 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm focus:outline-none focus:border-purple-accent transition-all"
                style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
              >
                {categories.map(cat => (
                  <option key={cat} value={cat} className="bg-black">
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
                className="w-full px-4 py-2.5 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-purple-accent transition-all"
                style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
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
                className="w-full px-4 py-2.5 bg-black/30 border border-purple-primary/30 rounded-lg text-white text-sm placeholder-white/30 focus:outline-none focus:border-purple-accent transition-all"
                style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
              />
            </div>

            <button
              onClick={handleGenerateQuote}
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-primary via-purple-accent to-purple-primary hover:from-purple-accent hover:via-purple-light hover:to-purple-accent rounded-full text-white text-sm font-medium shadow-lg shadow-purple-primary/30 hover:shadow-purple-light/70 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
              style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}
            >
              {loading ? 'Generating...' : 'Generate Quote'}
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center pb-6">
        <p className="text-white/60 text-sm font-light" style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}>
          Built by{' '}
          <a 
            href="https://ayanexus.dev/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-purple-light hover:text-purple-accent transition-colors font-medium"
          >
            AyaNexus
          </a>
          {' '}🦢
        </p>
      </footer>
    </div>
  );
};

export default QuoteGenerator;

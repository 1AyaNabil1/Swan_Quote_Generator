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
          <img 
            src="/img/AyO.png" 
            alt="Ayō" 
            className="w-10 h-10 object-contain"
          />
          <span className="text-xl font-semibold text-white" style={{ fontFamily: "'Poppins', 'Inter', sans-serif" }}>Ayō</span>
        </div>
      </header>

      {/* Two Column Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 px-8 pb-8">
        {/* Left Column - Quote Display */}
        <div className="flex items-center justify-center">
          <div className="w-full max-w-2xl border border-purple-primary/20 rounded-2xl p-8 md:p-12 min-h-[300px] flex items-center justify-center">
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
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-primary to-purple-accent hover:from-purple-accent hover:to-purple-light rounded-lg text-white text-sm font-medium shadow-lg shadow-purple-primary/30 hover:shadow-purple-accent/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
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

import React, { useState } from 'react';
import { Globe, Star, Zap, ArrowRight, Heart, X } from 'lucide-react';
import './App.css';

function App() {
  const [planets] = useState([
    {
      id: 1,
      name: "Kepler-452b",
      type: "Super Earth",
      keyFact: "Located in the habitable zone and could potentially support liquid water",
      icon: Globe,
      gradient: "from-blue-500 to-green-400"
    },
    {
      id: 2,
      name: "HD 209458b",
      type: "Hot Jupiter",
      keyFact: "First exoplanet discovered transiting its star, with extreme atmospheric winds",
      icon: Star,
      gradient: "from-orange-500 to-red-500"
    },
    {
      id: 3,
      name: "TRAPPIST-1e",
      type: "Terrestrial",
      keyFact: "One of seven Earth-sized planets in a ultra-cool dwarf star system",
      icon: Globe,
      gradient: "from-purple-500 to-pink-400"
    },
    {
      id: 4,
      name: "Proxima Centauri b",
      type: "Rocky Planet",
      keyFact: "Closest known exoplanet to Earth at just 4.24 light-years away",
      icon: Zap,
      gradient: "from-cyan-500 to-blue-500"
    }
  ]);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleNext = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % planets.length);
      setIsAnimating(false);
    }, 300);
  };

  const handlePrevious = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev - 1 + planets.length) % planets.length);
      setIsAnimating(false);
    }, 300);
  };

  const currentPlanet = planets[currentIndex];
  const IconComponent = currentPlanet.icon;

  return (
    <div className="app">
      <div className="app-header">
        <div className="header-content">
          <div className="logo">
            <Star className="logo-icon" />
            <h1>CosmicMatch</h1>
          </div>
          <p className="subtitle">Discover Your Perfect Cosmic Match</p>
        </div>
      </div>

      <div className="card-container">
        <div className={`planet-card ${isAnimating ? 'animating' : ''}`}>
          <div className={`card-gradient bg-gradient-to-br ${currentPlanet.gradient}`}></div>
          
          <div className="card-content">
            <div className="card-header">
              <div className="planet-icon">
                <IconComponent size={32} />
              </div>
              <div className="planet-info">
                <h2 className="planet-name">{currentPlanet.name}</h2>
                <span className="planet-type">{currentPlanet.type}</span>
              </div>
            </div>

            <div className="key-fact">
              <h3>Key Fact</h3>
              <p>{currentPlanet.keyFact}</p>
            </div>

            <div className="card-actions">
              <button className="action-btn reject-btn" onClick={handlePrevious}>
                <X size={24} />
                <span>Pass</span>
              </button>
              
              <div className="planet-indicator">
                <span>{currentIndex + 1}</span>
                <span className="separator">/</span>
                <span>{planets.length}</span>
              </div>

              <button className="action-btn like-btn" onClick={handleNext}>
                <Heart size={24} />
                <span>Like</span>
              </button>
            </div>
          </div>
        </div>

        <div className="navigation-hint">
          <ArrowRight className="hint-icon" />
          <span>Swipe or tap to explore more planets</span>
        </div>
      </div>

      <div className="background-stars">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="star"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`
            }}
          ></div>
        ))}
      </div>
    </div>
  );
}

export default App;